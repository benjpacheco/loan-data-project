import os
import pytest
import kaggle.api
import boto3
from unittest.mock import patch, MagicMock
from pipelines.make_dataset import download_kaggle_dataset, upload_to_s3

# @pytest.fixture
# def global_var():
#     pytest.DATA_PATH = "../data"

# Mock the kaggle.api.dataset_download_files function
@pytest.fixture
def mock_kaggle_api():
    with patch('kaggle.api.dataset_download_files') as mock:
        yield mock

# Mock the boto3.client function
@pytest.fixture
def mock_boto3_s3_client():
    with patch('boto3.client') as mock:
        yield mock

@pytest.fixture
def mock_env_user(monkeypatch):
    monkeypatch.setenv("DATA_PATH", "../../data")
    monkeypatch.setenv('BUCKET_NAME', 'artifacts-and-data-bp')
    monkeypatch.setenv('REFERENCE_DATA_KEY_PATH', '/ref')

# Test download_kaggle_dataset function
def test_download_kaggle_dataset(mock_env_user, mock_kaggle_api):
    username = 'xyz'
    key = '123455'
    download_kaggle_dataset(username, key)
    mock_kaggle_api.assert_called_once_with('utkarshx27/lending-club-loan-dataset', path='../../data', unzip=True)

# Test upload_to_s3 function
def test_upload_to_s3(mock_env_user, mock_boto3_s3_client):
    filename = 'loans_full_schema_clean.parquet'
    destination_path = '/reference'
    upload_to_s3(filename, destination_path)
    mock_boto3_s3_client.return_value.upload_file.assert_called_once_with(filename, 'artifacts-and-data-bp', os.path.join(destination_path, os.path.basename(filename)))
