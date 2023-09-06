import os
import json
import datetime

import boto3
import httpx
import pandas as pd
from prefect import flow, task, get_run_logger
from databases import Database
from sqlalchemy import Table, Column, String, DateTime, MetaData
from evidently.tabs import DataDriftTab
from prefect.schedules import IntervalSchedule
from evidently.dashboard import Dashboard

logger = get_run_logger()


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


# Function to fetch the last predictions from the database
async def load_last_predictions(window_size: int) -> pd.DataFrame:
    query = (
        predictions.select()
        .order_by(predictions.c.created_at.desc())
        .limit(window_size)
    )
    rows = await database.fetch_all(query)
    return pd.DataFrame(rows)


@task
async def load_current_data(window_size: int) -> pd.DataFrame:
    current_data = await load_last_predictions(
        window_size
    )  # Fetch current data from the database
    return current_data


@task
def load_data_from_s3(bucket_name, key_path):
    s3 = boto3.client('s3')
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=key_path)
        return pd.read_parquet(obj['Body'])
    except Exception as e:
        logger.error(f"Error loading data from S3: {e}")
        raise


@task
def detect_drift(reference_data: pd.DataFrame, current_data: pd.DataFrame) -> bool:
    column_mapping = {
        'numerical_features': reference_data.select_dtypes(
            include=['int64', 'float64']
        ).columns.tolist(),
        'categorical_features': reference_data.select_dtypes(
            include=['object']
        ).columns.tolist(),
        'target': 'loan_status',
    }

    data_drift_dashboard = Dashboard(tabs=[DataDriftTab])
    data_drift_dashboard.calculate(
        reference_data, current_data, column_mapping=column_mapping
    )
    drift_detected = (
        data_drift_dashboard.get_by_tab_name("Data Drift").get_metrics()["data_drift"][
            "value"
        ]
        > 0.05
    )
    return drift_detected


@task
def run_training_pipeline():
    try:
        # Send a POST request to the Flask app's trigger endpoint
        response = httpx.post("http://mlflow_server:5001/trigger-training")
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise RuntimeError(f"Error triggering training: {e}") from e


@flow
def drift_detection_and_retraining(
    reference_data: pd.DataFrame, database_window_size: int
):
    current_data = load_current_data(database_window_size)
    drift = detect_drift(reference_data, current_data)
    if drift:
        run_training_pipeline()


def main():
    ARTIFACT_BUCKET_NAME = os.environ.get("ARTIFACT_BUCKET_NAME", "default_bucket_name")
    REFERENCE_DATA_KEY_PATH = os.environ.get(
        "REFERENCE_DATA_KEY_PATH", "default_reference_data_key_path"
    )

    # Load reference data using the load_data_from_s3 function
    reference_data = load_data_from_s3(ARTIFACT_BUCKET_NAME, REFERENCE_DATA_KEY_PATH)

    schedule = IntervalSchedule(
        start_date=datetime.datetime.utcnow() + datetime.timedelta(seconds=1),
        interval=datetime.timedelta(weeks=1),
    )

    drift_detection_and_retraining.schedule = schedule
    drift_detection_and_retraining.register("Drift Detection and Retraining Project")
    drift_detection_and_retraining.run(
        reference_data=reference_data, database_window_size=3000
    )


if __name__ == "__main__":
    main()
