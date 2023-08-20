import pytest
import boto3
from unittest.mock import MagicMock, Mock, patch
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score
from io import BytesIO
import os
import sys

sys.path.append(os.path.dirname("../src/pipelines"))

from pipelines.train import LoanPredictionModel, train_val_test_split, load_data_from_s3, post_training_tasks

# Mock Boto3 client
class MockS3Client:
    def __init__(self):
        pass

    def get_object(self, Bucket, Key):
        data = {'loan_status': np.random.randint(0, 2, 100), 'feature1': np.random.rand(100), 'feature2': np.random.rand(100)}
        return {'Body': BytesIO(pd.DataFrame(data).to_parquet())}

@pytest.fixture
def mock_boto3_s3_client(monkeypatch):
    mock_client = MockS3Client()
    monkeypatch.setattr('boto3.client', Mock(return_value=mock_client))
    return mock_client

# Test LoanPredictionModel methods
def test_train_and_log(mock_boto3_s3_client):
    data = pd.DataFrame({'loan_status': np.random.randint(0, 2, 100), 'feature1': np.random.rand(100), 'feature2': np.random.rand(100)})
    model = LoanPredictionModel(data)
    
    # First split to create train_val and test sets
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        data.drop(columns=['loan_status']),
        data['loan_status'],
        test_size=0.2,
        random_state=42
    )

    # Second split to create train and val sets from train_val
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=0.25,
        random_state=42
    )
    
    with pytest.raises(Exception):
        model.train_and_log(X_train, y_train, X_val, y_val, X_test, y_test)


def test_log_metrics_and_model():
    data = pd.DataFrame({'loan_status': [0, 1], 'feature1': [0.5, 0.7]})
    model = LoanPredictionModel(data)
    pipeline = model._build_preprocessor()
    X_test, y_test = data.drop(columns=['loan_status']), data['loan_status']
    best_threshold = 0.5
    model._log_metrics_and_model(pipeline, X_test, y_test, best_threshold)

# Test other methods
def test_train_val_test_split():
    X = pd.DataFrame({'feature1': np.random.rand(100), 'feature2': np.random.rand(100)})
    y = pd.Series(np.random.randint(0, 2, 100))  # Generate random binary labels
    train_size = 0.6
    val_size = 0.2
    test_size = 0.2
    random_state = 42
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split(X, y, train_size, val_size, test_size, random_state)
    assert len(X_train) + len(X_val) + len(X_test) == len(X)
    assert len(y_train) + len(y_val) + len(y_test) == len(y)

# Test load_data_from_s3 function
def test_load_data_from_s3(mock_boto3_s3_client):
    bucket_name = 'mock_bucket'
    key_path = 'mock_key_path'

    # Mock the return value of s3.get_object()
    mock_s3_client = mock_boto3_s3_client
    mock_s3_client.get_object.side_effect = {'Body': Mock()}

    # Mock pd.read_parquet
    mock_read_parquet = Mock(return_value=pd.DataFrame())
    with patch('pandas.read_parquet', mock_read_parquet):
        data = load_data_from_s3(bucket_name, key_path)
        
        # Assertions
        assert isinstance(data, pd.DataFrame)
        mock_s3_client.get_object.assert_called_once_with(Bucket=bucket_name, Key=key_path)
        mock_read_parquet.assert_called_once_with(mock_s3_client.get_object.return_value['Body'])


def test_post_training_tasks(mocker):
    runs_mock = mocker.Mock()
    runs_mock.sort_values.return_value = pd.DataFrame({'start_time': ['2023-08-17 10:00:00']})
    mocker.patch('mlflow.search_runs', return_value=runs_mock)
    
    client_mock = mocker.Mock()
    mocker.patch('mlflow.tracking.MlflowClient', return_value=client_mock)
    
    post_training_tasks()
    client_mock.transition_model_version_stage.assert_called_once()

    mlflow.set_tracking_uri.assert_called_once()
    mlflow.set_experiment.assert_called_once()
    train_val_test_split.assert_called_once()
    train.LoanPredictionModel.assert_called_once()
    model_mock.train_and_log.assert_called_once()
    post_training_tasks.assert_called_once()


