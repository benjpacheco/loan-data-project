import os
from unittest.mock import MagicMock, patch

import kaggle
import pytest

from pipelines.make_dataset import upload_to_s3, download_kaggle_dataset


@pytest.fixture
def mock_kaggle_api():
    with patch('kaggle.api.dataset_download_files') as mock:
        yield mock


# Mock the boto3.client function
@pytest.fixture
def mock_boto3_s3_client():
    with patch('boto3.client') as mock:
        yield mock.return_value  # Return the mock's return value


@pytest.fixture
def mock_env_user(monkeypatch):
    monkeypatch.setenv("DATA_PATH", "../../data")
    monkeypatch.setenv('ARTIFACT_BUCKET_NAME', 'artifacts-and-data-bp')
    monkeypatch.setenv('REFERENCE_DATA_KEY_PATH', '/ref')


# Test download_kaggle_dataset function
def test_download_kaggle_dataset(mock_env_user, mock_kaggle_api):
    username = 'xyz'
    key = '123455'
    download_kaggle_dataset(username, key)
    mock_kaggle_api.assert_called_once_with(
        'utkarshx27/lending-club-loan-dataset', path='../../data', unzip=True
    )


def test_upload_to_s3(mock_env_user, mock_boto3_s3_client):
    filename = 'loans_full_schema_clean.parquet'
    destination_path = '/reference'

    with patch('os.getenv', return_value='artifacts-and-data-bp'):
        upload_to_s3(filename, destination_path)

    mock_boto3_s3_client.return_value.upload_file.assert_called_once_with(
        filename,
        'artifacts-and-data-bp',  # This should match the value from os.getenv
        os.path.join(destination_path, os.path.basename(filename)),
    )
