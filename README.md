# Loan Default Prediction Project

## Objective

The objective of this project is to predict whether a loan will default (charged off). The primary goal is to optimize for recall over precision to minimize risk and avoid bad loans.

## Project Structure
```
├── .github/workflows
│ ├── cd-deploy.yml
│ ├── ci-tests.yml
├── fastapi_backend
│ ├── app.py
│ ├── Dockerfile
│ ├── models.py
├── infrastructure
│ ├── main.tf
│ ├── outputs.tf
│ ├── variables.tf
│ ├── modules
│ ├── terraform.tfvars
├── notebooks
│ ├── loan_data_modeling
│ ├── loan_data_eda
│ ├── loan_data_monitoring
├── orchestration
│ ├── detect_drift.py
│ ├── Dockerfile
│ ├── run_prefect_workflow.sh
├── src
│ ├── pipelines
│ │ ├── tests
│ │ ├── train_trigger.py
│ │ ├── train.py
│ │ ├── Dockerfile
│ │ ├── make_dataset.py
│ │ ├── entrypoint.sh
├── streamlit_frontend
│ ├── Dockerfile
│ ├── streamlit_app.py
├── .gitignore
├── .pre-commit-config.yaml
├── docker-compose.yaml
├── Pipfile
├── Pipfile.lock
├── pyproject.toml
├── README.md
```

## Data Source

The dataset used for this project can be found on Kaggle: [Loan Dataset](https://www.kaggle.com/datasets/utkarshx27/lending-club-loan-dataset)

## Tools

- Terraform
- FastAPI
- Streamlit
- MLflow
- Prefect
- Evidently
- AWS

## Infrastructure

Terraform provisions various AWS services, including:
- EC2 instance for hosting the prediction service
- RDS instances for storing predictions and metadata for MLflow
- S3 bucket for artifacts and data storage
- VPC (Virtual Private Cloud) for EC2 and RDS to communicate within the same network
- ECR (Elastic Container Registry) to store Docker images
- IAM roles and policies needed for the infrastructure components to function

## Components

- **FastAPI**: Responsible for capturing POST requests from the Streamlit app to invoke predictions. Background tasks store predictions in an RDS instance.
- **Streamlit**: Frontend UI displaying monitoring metrics and making predictions by sending POST requests to the FastAPI backend.
- **MLflow**: Handles experimentation and model registry, storing artifacts in the provided S3 bucket.
- **Prefect**: Orchestrates tasks, particularly in the drift detection and retraining pipeline, sends a request to trigger retraining if drift is detected.
- **Evidently**: Provides monitoring reports and enables functionality within the Streamlit app.

## Reproducibility

1. Create an AWS account.
2. Create an IAM user called "superuser" and attach policies: 
   - AmazonEC2ContainerRegistryFullAccess
   - AmazonEC2FullAccess
   - AmazonS3FullAccess
   - IAMFullAccess

then create a new policy and replace <YOUR_REGION>, <YOUR_ACCOUNT_ID> and attach it to superuser

you will also have to edit the terraform files, specifically in the IAM module

```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": "secretsmanager:DescribeSecret",
			"Resource": "arn:aws:secretsmanager:<YOUR_REGION>:<YOUR_ACCOUNT_ID>:secret:*"
		},
		{
			"Effect": "Allow",<YOUR_ACCOUNT_ID>
			"Action": [
				"secretsmanager:CreateSecret",
				"secretsmanager:DeleteSecret",
				"secretsmanager:PutSecretValue",
				"secretsmanager:GetSecretValue"
			],
			"Resource": "arn:aws:secretsmanager:<YOUR_REGION>:<YOUR_ACCOUNT_ID>:secret:*"
		},
		{
			"Effect": "Allow",
			"Action": "secretsmanager:GetResourcePolicy",
			"Resource": "arn:aws:secretsmanager:<YOUR_REGION>:<YOUR_ACCOUNT_ID>:secret:*"
		},
		{
			"Effect": "Allow",
			"Action": [
				"rds:CreateDBInstance",
				"rds:DeleteDBInstance",
				"rds:DescribeDBInstances",
				"rds:ModifyDBInstance",
				"rds:RebootDBInstance",
				"rds:CreateDBSubnetGroup",
				"rds:ModifyDBSubnetGroup",
				"rds:DeleteDBSubnetGroup",
				"rds:AddTagsToResource",
				"rds:DescribeDBSubnetGroups",
				"rds:ListTagsForResource"
			],
			"Resource": [
				"arn:aws:rds:<YOUR_REGION>:<YOUR_ACCOUNT_ID>:pg:*",
				"arn:aws:rds:<YOUR_REGION>:<YOUR_ACCOUNT_ID>:db:*",
				"arn:aws:rds:<YOUR_REGION>:<YOUR_ACCOUNT_ID>:og:*",
				"arn:aws:rds:<YOUR_REGION>:<YOUR_ACCOUNT_ID>:subgrp:rds-subnet-group"
			]
		}
	]
}
```
3. Create an access key and secret key ID for the "superuser" user and add them to the repository for CI/CD pipeline.
4. Create a Kaggle account and get the user and API key, and add them to the repository.
5. Trigger the CI/CD pipeline by merging a commit from any feature branch into the develop branch.
6. Wait for AWS services to be provisioned by Terraform.
7. Access the FastAPI prediction service using the output from Terraform: `http://<EC2_Public_IP>:9696`.

## Fixes To Do

- Fix github actions error related to  jq: error (at <stdin>:1): Cannot index string with string "username"
Error: Process completed with exit code 5.
- Fix tests
- Fix linting
- Perform integration tests

