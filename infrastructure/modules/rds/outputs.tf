
output "mlflow_db_endpoint" {
  value = aws_db_instance.mlflow_database.endpoint
}

output "fastapi_db_endpoint" {
  value = aws_db_instance.fastapi_database.endpoint
}

output "mlflow_database_credentials" {
  value = jsondecode(aws_secretsmanager_secret_version.mlflow_db_credentials.secret_string)
}


output "mlflow_database_name" {
  value = aws_db_instance.mlflow_database.db_name
}
