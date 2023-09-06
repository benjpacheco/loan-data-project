# Use a base image that has Python and necessary dependencies
FROM python:3.9.17-slim

RUN pip install -U pip

# Set the working directory
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --ignore-installed -r requirements.txt

# Copy files into the container
COPY train.py /app/train.py
COPY train_trigger.py /app/train_trigger.py
COPY make_dataset.py /app/make_dataset.py

# Expose the MLflow server port
EXPOSE 5000 5001

# Define build-time arguments
ARG MLFLOW_DB_ENDPOINT
ARG MLFLOW_DB_NAME
ARG MLFLOW_DB_USERNAME
ARG MLFLOW_DB_PASSWORD
ARG ARTIFACT_BUCKET_NAME
ARG KAGGLE_USERNAME
ARG KAGGLE_API_KEY

# Set the default environment variables for MLflow and Kaggle
ENV KAGGLE_USERNAME=$KAGGLE_USERNAME
ENV KAGGLE_API_KEY=$KAGGLE_API_KEY
ENV MLFLOW_SERVER_URI="0.0.0.0"
ENV MLFLOW_SERVER_PORT="5000"
ENV MLFLOW_BACKEND_URI="postgresql://$MLFLOW_DB_USERNAME:$MLFLOW_DB_PASSWORD@$MLFLOW_DB_ENDPOINT:5432/$MLFLOW_DB_NAME"
ENV MLFLOW_ARTIFACT_ROOT="s3://$ARTIFACT_BUCKET_NAME"

RUN echo $KAGGLE_USERNAME && echo $KAGGLE_API_KEY

# Run make_dataset.py
RUN python make_dataset.py --username $KAGGLE_USERNAME --key $KAGGLE_API_KEY

# Copy the entrypoint.sh script into the container
COPY entrypoint.sh /app/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]