#!/bin/bash

# Run the MLflow server in the background
mlflow server \
    --host $MLFLOW_SERVER_URI \
    --port $MLFLOW_SERVER_PORT \
    --backend-store-uri $MLFLOW_BACKEND_URI \
    --default-artifact-root $MLFLOW_ARTIFACT_ROOT &

# Run train.py and train_trigger.py sequentially
python train.py
python train_trigger.py
