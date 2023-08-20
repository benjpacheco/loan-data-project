import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.metrics import f1_score, precision_score, recall_score
import boto3
import mlflow
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoanPredictionModel:

    def __init__(self, data_frame):
        self.df = data_frame
        self.X, self.y = self._split_features_labels()
        self.n_classes = 2
        self.class_weights = self._compute_class_weights()
        self.categorical_features = self.X.select_dtypes(include=['object']).columns.tolist()
        self.numerical_features = self.X.select_dtypes(include=['int64', 'float64']).columns.tolist()
        self.preprocessor = self._build_preprocessor()
        self.params = {
            'C': 0.31303873900972606,
            'class_weight': self.class_weights,
            'penalty': 'l1',
            'solver': 'liblinear',
            'random_state': 42
        }

    def _split_features_labels(self):
        return self.df.drop(columns=['loan_status']), self.df['loan_status']

    def _compute_class_weights(self):
        count_majority_class = self.df['loan_status'].value_counts()[0]
        count_minority_class = self.df['loan_status'].value_counts()[1]
        total_samples = count_majority_class + count_minority_class
        weight_majority_class = total_samples / (self.n_classes * count_majority_class)
        weight_minority_class = total_samples / (self.n_classes * count_minority_class)
        return {0: weight_majority_class, 1: weight_minority_class}

    def _build_preprocessor(self):
        numerical_transformer = StandardScaler(with_mean=False)
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')
        return make_column_transformer(
            (numerical_transformer, self.numerical_features),
            (categorical_transformer, self.categorical_features)
        )

    def train_and_log(self, X_train, y_train, X_val, y_val, X_test, y_test):
        mlflow.log_params(self.params)
        pipeline = make_pipeline(self.preprocessor, LogisticRegression(**self.params))
        pipeline.fit(X_train, y_train)
        best_threshold = self._find_best_threshold(pipeline, X_val, y_val)
        self._log_metrics_and_model(pipeline, X_test, y_test, best_threshold)

    def _find_best_threshold(self, pipeline, X_val, y_val):
        probabilities = pipeline.predict_proba(X_val)[:, 1]
        thresholds = np.linspace(0, 1, 100)
        scores = [
            f1_score(y_val, [1 if prob > threshold else 0 for prob in probabilities])
            for threshold in thresholds
        ]
        return thresholds[np.argmax(scores)]

    def _log_metrics_and_model(self, pipeline, X_test, y_test, best_threshold):
        with mlflow.start_run():
            y_preds = pipeline.predict_proba(X_test)[:, 1]
            y_preds_threshold = [1 if prob > best_threshold else 0 for prob in y_preds]
            f1 = f1_score(y_test, y_preds_threshold)
            precision = precision_score(y_test, y_preds_threshold)
            recall = recall_score(y_test, y_preds_threshold)

            mlflow.log_metric("f1-score", f1)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            mlflow.sklearn.log_model(pipeline, artifact_path="model")


def train_val_test_split(X, y, train_size, val_size, test_size, random_state):
    if train_size + val_size + test_size != 1:
        raise ValueError("train_size and val_size should sum up to 1")

    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size = test_size, random_state=random_state, stratify=y)
    relative_train_size = train_size / (val_size + train_size)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val,
                                                      train_size = relative_train_size, test_size = 1-relative_train_size, random_state=random_state, stratify=y_train_val)
    return X_train, X_val, X_test, y_train, y_val, y_test

def load_data_from_s3(bucket_name, key_path):
    s3 = boto3.client('s3')
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=key_path)
        return pd.read_parquet(obj['Body'])
    except Exception as e:
        logger.error(f"Error loading data from S3: {e}")
        raise

def post_training_tasks():
    # Retrieve a list of all runs
    runs = mlflow.search_runs()

    # Sort runs by start time and get the most recent run
    latest_run = runs.sort_values(by="start_time", ascending=False).iloc[0]

    # If you want to print the details of the latest run
    print(latest_run)

    # Get the run_id of the latest run
    latest_run_id = latest_run["run_id"]
    print(f"Latest Run ID: {latest_run_id}")

    model_uri = f"runs:/{latest_run_id}/model"
    model_details = mlflow.register_model(model_uri, "loan-prediction")

    client = mlflow.tracking.MlflowClient()
    # Transition model version to 'Production' stage
    client.transition_model_version_stage(
        name="loan-prediction",
        version=model_details.version,
        stage="Production",
    )


def main():
    ARTIFACT_BUCKET_NAME = os.environ.get("ARTIFACT_BUCKET_NAME", "your_default_bucket_name")
    REFERENCE_DATA_KEY_PATH = os.environ.get("REFERENCE_DATA_KEY_PATH", "your_default_key_path")
    TRACKING_URI = os.environ.get("TRACKING_URI", "http://127.0.0.1:5000")
    
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment("loan-prediction-experiment")
    
    # Use the load_data_from_s3 directly in the main function
    data = load_data_from_s3(ARTIFACT_BUCKET_NAME, REFERENCE_DATA_KEY_PATH)
    
    # Pass the dataframe directly to the LoanPredictionModel class
    model = LoanPredictionModel(data)
    
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split(
        model.X, model.y, train_size=0.8, val_size=0.1, test_size=0.1, random_state=42
    )

    logger.info("Training and logging model...")
    model.train_and_log(X_train, y_train, X_val, y_val, X_test, y_test)
    
    logger.info("Executing post-training tasks...")
    post_training_tasks()

if __name__ == "__main__":
    main()

