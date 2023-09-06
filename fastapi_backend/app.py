# Standard library imports
import os
import json
import logging
from datetime import datetime

# Third party imports
import boto3
import mlflow
import pandas as pd
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from databases import Database
from evidently import ColumnMapping
from sqlalchemy import Table, Column, String, DateTime, MetaData
from evidently.report import Report
from evidently.metrics import DatasetDriftMetric, DatasetMissingValuesMetric
from fastapi.responses import FileResponse
from evidently.metric_preset import TargetDriftPreset, ClassificationPreset

# Local/application-specific imports
from models import LoanData


# Set up a connection to the Postgres RDS instance.
# Get the RDS instance information, including the endpoint
def get_rds_endpoint(instance_identifier: str) -> str:
    """Fetch the endpoint for a given RDS instance identifier."""
    rds_client = boto3.client('rds')
    rds_instances = rds_client.describe_db_instances(
        DBInstanceIdentifier=instance_identifier
    )
    return rds_instances['DBInstances'][0]['Endpoint']['Address']


def get_db_credentials(secret_name: str) -> dict:
    """Fetch DB credentials from AWS Secrets Manager."""
    session = boto3.session.Session()
    secretsmanager = session.client(service_name='secretsmanager')
    secret = secretsmanager.get_secret_value(SecretId=secret_name)
    return json.loads(secret['SecretString'])


# Fetch FastAPI DB credentials
fastapi_db_credentials = get_db_credentials('fastapi_db_credentials')

DB_USER = fastapi_db_credentials["username"]
DB_PASSWORD = fastapi_db_credentials["password"]
RDS_ENDPOINT = get_rds_endpoint('fastapi_db')

# Set up the connection string to the Postgres RDS instance using the fetched data
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{RDS_ENDPOINT}:5432/fastapi_db"


database = Database(DATABASE_URL)
metadata = MetaData()

predictions = Table(
    "predictions",
    metadata,
    Column("created_at", DateTime, primary_key=True),
    Column("input", String),
    Column("output", String),
)

# Constants for S3 data fetching
BUCKET_NAME = os.environ.get("BUCKET_NAME", "artifacts-and-data-bp")
REFERENCE_DATA_KEY_PATH = os.environ.get("REFERENCE_DATA_KEY_PATH", "/reference")

# Initialize the S3 client
s3 = boto3.client('s3')

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format='FASTAPI_APP - %(asctime)s - %(levelname)s - %(message)s'
)

RUN_ID = str(os.getenv('RUN_ID', 'decc0e5be9024909bd87d1c9112e237b'))
logged_model = f's3://{BUCKET_NAME}/3/{RUN_ID}/artifacts/model'


# Background Task for Saving Predictions
async def save_to_database(input_data: dict, output: dict) -> None:
    query = predictions.insert().values(
        created_at=datetime.now(), input=str(input_data), output=str(output)
    )
    await database.execute(query)


# Function to fetch the last predictions from the database
async def load_last_predictions(window_size: int) -> pd.DataFrame:
    query = (
        predictions.select()
        .order_by(predictions.c.created_at.desc())
        .limit(window_size)
    )
    rows = await database.fetch_all(query)
    return pd.DataFrame(rows)


# Function to fetch data from S3
def load_data_from_s3(bucket_name, key_path):
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=key_path)
        return pd.read_parquet(obj['Body'])
    except Exception as e:
        logger.error("Error loading data from S3: %s", e)
        raise


def get_column_mapping(target_col, prediction_col, num_features, cat_features):
    column_mapping = ColumnMapping()
    column_mapping.target = target_col
    column_mapping.prediction = prediction_col
    column_mapping.numerical_features = num_features
    column_mapping.categorical_features = cat_features
    return column_mapping


# model = mlflow.pyfunc.load_model(logged_model)
model = mlflow.sklearn.load_model(logged_model)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/')
def index():
    return {'message': 'Hello'}


@app.get('/home')
def get_home():
    return {'message': 'You are Home'}


@app.post('/predict')
def predict_chargedoff(data: LoanData, background_tasks: BackgroundTasks):
    data_dict = data.dict()
    X = pd.DataFrame([list(data_dict.values())], columns=data_dict.keys())
    prediction = model.predict(X)

    preds = "Charged Off" if prediction[0] else "Not Charged Off"
    background_tasks.add_task(save_to_database, input_data=data_dict, output=preds)
    return {'prediction': preds}


@app.get('/monitor-model')
async def monitor_model_performance(window_size: int = 3000) -> FileResponse:
    current_data = await load_last_predictions(window_size)
    reference_data = load_data_from_s3(BUCKET_NAME, REFERENCE_DATA_KEY_PATH)

    categorical_features = current_data.select_dtypes(
        include=['object']
    ).columns.tolist()
    numerical_features = current_data.select_dtypes(
        include=['int64', 'float64']
    ).columns.tolist()

    column_mapping = get_column_mapping(
        target_col="loan_status",
        prediction_col="prediction",
        num_features=numerical_features,
        cat_features=categorical_features,
    )

    model_performance_report = Report(
        metrics=[
            DatasetDriftMetric(),
            DatasetMissingValuesMetric(),
            ClassificationPreset(probas_threshold=0.05050505050505051),
        ]
    )

    model_performance_report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping,
    )

    report_path = '../reports/model_performance.html'
    model_performance_report.save_html(report_path)
    return FileResponse(report_path)


@app.get('/monitor-target')
async def monitor_target_drift(window_size: int = 3000) -> FileResponse:
    current_data = await load_last_predictions(window_size)
    reference_data = load_data_from_s3(BUCKET_NAME, REFERENCE_DATA_KEY_PATH)

    categorical_features = current_data.select_dtypes(
        include=['object']
    ).columns.tolist()
    numerical_features = current_data.select_dtypes(
        include=['int64', 'float64']
    ).columns.tolist()

    column_mapping = get_column_mapping(
        target_col="loan_status",
        prediction_col="prediction",
        num_features=numerical_features,
        cat_features=categorical_features,
    )

    target_drift_report = Report(metrics=[TargetDriftPreset()])
    target_drift_report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping,
    )

    report_path = '../reports/target_drift.html'
    target_drift_report.save_html(report_path)
    return FileResponse(report_path)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=9696)
