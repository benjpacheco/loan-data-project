#!/bin/bash

# Initialize the Prefect project
prefect project init

# Create a Prefect worker in the background
prefect worker start -p drift-detect-worker -t process &

# Wait for a few seconds to ensure the worker is up and running
sleep 5

# Deploy the Prefect flow
prefect deploy detect_drift.py:drift_detection_and_retraining -n 'drift-detection' -p drift-detect-worker

# Start a Prefect worker
prefect worker start -p drift-detect-worker &

# Wait for a few seconds to ensure the worker is up and running
sleep 5

# Run the deployment flow
prefect deployment run drift_detection_and_retraining/drift-detection
