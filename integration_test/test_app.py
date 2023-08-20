# tests/test_app.py
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app

client = TestClient(app)

# Mocked data for testing
mock_db_credentials = {"username": "test_user", "password": "test_password"}
mock_rds_endpoint = "mocked_rds_endpoint"
mock_db_instance = {"DBInstances": [{"Endpoint": {"Address": mock_rds_endpoint}}]}
mock_reference_data = "mocked_reference_data"
mock_data = "mocked_data"

@patch("app.get_db_credentials")
@patch("app.get_rds_endpoint")
@patch("app.load_data_from_s3")
def test_startup(mock_load_data_from_s3, mock_get_rds_endpoint, mock_get_db_credentials):
    mock_get_db_credentials.return_value = mock_db_credentials
    mock_get_rds_endpoint.return_value = mock_rds_endpoint
    mock_load_data_from_s3.return_value = mock_reference_data

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}

@patch("app.get_db_credentials")
@patch("app.get_rds_endpoint")
@patch("app.load_data_from_s3")
@patch("app.mlflow.sklearn.load_model")
@patch("app.load_last_predictions")
def test_monitor_model_performance(
    mock_load_last_predictions, mock_mlflow_load_model, mock_load_data_from_s3,
    mock_get_rds_endpoint, mock_get_db_credentials
):
    mock_get_db_credentials.return_value = mock_db_credentials
    mock_get_rds_endpoint.return_value = mock_rds_endpoint
    mock_load_data_from_s3.return_value = mock_reference_data
    mock_mlflow_load_model.return_value = MagicMock(predict=MagicMock(return_value=[0]))

    response = client.get("/monitor-model")

    assert response.status_code == 200
    assert os.path.exists("../reports/model_performance.html")

@patch("app.get_db_credentials")
@patch("app.get_rds_endpoint")
@patch("app.load_data_from_s3")
@patch("app.mlflow.sklearn.load_model")
@patch("app.load_last_predictions")
def test_predict_chargedoff(
    mock_load_last_predictions, mock_mlflow_load_model, mock_load_data_from_s3,
    mock_get_rds_endpoint, mock_get_db_credentials
):
    mock_get_db_credentials.return_value = mock_db_credentials
    mock_get_rds_endpoint.return_value = mock_rds_endpoint
    mock_load_data_from_s3.return_value = mock_reference_data
    mock_mlflow_load_model.return_value = MagicMock(predict=MagicMock(return_value=[0]))

    response = client.post("/predict", json={"feature_1": 1, "feature_2": 2})

    assert response.status_code == 200
    assert response.json() == {"prediction": "Not Charged Off"}

# Add more tests for other routes and functionalities in app.py
