import os
import logging
from typing import Any, Dict, Tuple

import boto3
import numpy as np
import mlflow
import pandas as pd
from sklearn.compose import make_column_transformer
from sklearn.metrics import f1_score, recall_score, precision_score
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoanPredictionModel:
    def __init__(self, data_frame: pd.DataFrame):
        self.df = data_frame
        self.X, self.y = self._split_features_labels()
        self.n_classes = 2
        self.class_weights = self._compute_class_weights()
        self.categorical_features = self.X.select_dtypes(
            include=['object']
        ).columns.tolist()
        self.numerical_features = self.X.select_dtypes(
            include=['int64', 'float64']
        ).columns.tolist()
        self.preprocessor = self._build_preprocessor()
        self.params = {
            'C': 0.31303873900972606,
            'class_weight': self.class_weights,
            'penalty': 'l1',
            'solver': 'liblinear',
            'random_state': 42,
        }

    def _split_features_labels(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Split dataframe into features and labels."""
        return self.df.drop(columns=['loan_status']), self.df['loan_status']

    def _compute_class_weights(self) -> Dict[int, float]:
        """Compute class weights for imbalanced dataset."""
        count_majority_class = self.df['loan_status'].value_counts()[0]
        count_minority_class = self.df['loan_status'].value_counts()[1]
        total_samples = count_majority_class + count_minority_class
        weight_majority_class = total_samples / (self.n_classes * count_majority_class)
        weight_minority_class = total_samples / (self.n_classes * count_minority_class)
        return {0: weight_majority_class, 1: weight_minority_class}

    def _build_preprocessor(self) -> Any:
        """Build column transformer for preprocessing."""
        numerical_transformer = StandardScaler(with_mean=False)
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')
        return make_column_transformer(
            (numerical_transformer, self.numerical_features),
            (categorical_transformer, self.categorical_features),
        )

    def train_and_log(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> None:
        """Train the model and log parameters, metrics, and the model itself."""
        mlflow.log_params(self.params)
        pipeline = make_pipeline(self.preprocessor, LogisticRegression(**self.params))
        pipeline.fit(X_train, y_train)
        best_threshold = self._find_best_threshold(pipeline, X_val, y_val)
        self._log_metrics_and_model(pipeline, X_test, y_test, best_threshold)

    def _find_best_threshold(
        self, pipeline: Any, X_val: pd.DataFrame, y_val: pd.Series
    ) -> float:
        """Find the best threshold for classification based on F1 score."""
        probabilities = pipeline.predict_proba(X_val)[:, 1]
        thresholds = np.linspace(0, 1, 100)
        scores = [
            f1_score(y_val, [1 if prob > threshold else 0 for prob in probabilities])
            for threshold in thresholds
        ]
        return thresholds[np.argmax(scores)]

    def _log_metrics_and_model(
        self,
        pipeline: Any,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        best_threshold: float,
    ) -> None:
        """Log model metrics and save the model to mlflow."""
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


def train_val_test_split(
    X: pd.DataFrame,
    y: pd.Series,
    train_size: float,
    val_size: float,
    test_size: float,
    random_state: int,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """Split the dataset into train, validation and test sets."""
    if train_size + val_size + test_size != 1:
        raise ValueError("train_size, val_size, and test_size should sum up to 1")

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    relative_train_size = train_size / (val_size + train_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        train_size=relative_train_size,
        test_size=1 - relative_train_size,
        random_state=random_state,
        stratify=y_train_val,
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def load_data_from_s3(bucket_name: str, key_path: str) -> pd.DataFrame:
    """Load data from S3 and return as a dataframe."""
    s3 = boto3.client('s3')
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=key_path)
        return pd.read_parquet(obj['Body'])
    except Exception as e:
        logger.error("Error loading data from S3: %s", e)
        raise


def post_training_tasks() -> None:
    """Execute post-training tasks including model registration and transition to production."""
    # Retrieve a list of all runs
    runs = mlflow.search_runs()

    # Sort runs by start time and get the most recent run
    latest_run = runs.sort_values(by="start_time", ascending=False).iloc[0]

    # Get the run_id of the latest run
    latest_run_id = latest_run["run_id"]

    model_uri = f"runs:/{latest_run_id}/model"
    model_details = mlflow.register_model(model_uri, "loan-prediction")

    client = mlflow.tracking.MlflowClient()
    # Transition model version to 'Production' stage
    client.transition_model_version_stage(
        name="loan-prediction",
        version=model_details.version,
        stage="Production",
    )


def main() -> None:
    """Main function to execute the entire flow of training, logging, and post-training tasks."""
    ARTIFACT_BUCKET_NAME = os.environ.get(
        "ARTIFACT_BUCKET_NAME", "your_default_bucket_name"
    )
    REFERENCE_DATA_KEY_PATH = os.environ.get(
        "REFERENCE_DATA_KEY_PATH", "your_default_key_path"
    )
    TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "your_default_mlflow_uri")
    RANDOM_STATE = int(os.environ.get("RANDOM_STATE", 42))

    mlflow.set_tracking_uri(TRACKING_URI)

    # Load data
    df = load_data_from_s3(
        bucket_name=ARTIFACT_BUCKET_NAME, key_path=REFERENCE_DATA_KEY_PATH
    )
    logger.info("Data loaded from S3 successfully.")

    # Splitting data
    loan_model = LoanPredictionModel(df)
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split(
        loan_model.X,
        loan_model.y,
        train_size=0.7,
        val_size=0.15,
        test_size=0.15,
        random_state=RANDOM_STATE,
    )
    logger.info("Data splitted successfully.")

    # Train, log and post-training tasks
    loan_model.train_and_log(X_train, y_train, X_val, y_val, X_test, y_test)
    post_training_tasks()
    logger.info("Training and post-training tasks completed successfully.")


if __name__ == "__main__":
    main()
