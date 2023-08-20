resource "aws_db_instance" "mlflow_database" {
  allocated_storage    = 20
  max_allocated_storage = 1000  # maximum storage threshold 
  storage_type         = "gp2"
  engine               = "PostgreSQL"
  engine_version       = "14.7"
  instance_class       = "db.t3.micro"
  db_name                 = "mlflow_db"
  parameter_group_name = "default.postgres14"
  # master_username      = jsondecode("${aws_secretsmanager_secret_version.mlflow_db_credentials.secret_string}")["username"]
  # master_password      = jsondecode("${aws_secretsmanager_secret_version.mlflow_db_credentials.secret_string}")["password"]
  skip_final_snapshot  = true
  vpc_security_group_ids = [var.rds_sg]
  backup_window        = "05:00-09:00"
  backup_retention_period = 7
  auto_minor_version_upgrade = true
  depends_on = [aws_secretsmanager_secret.mlflow_db_credentials]
}

resource "aws_db_instance" "fastapi_database" {
  allocated_storage    = 20
  storage_type         = "gp2"
  max_allocated_storage = 1000  # maximum storage threshold 
  engine               = "PostgreSQL"
  engine_version       = "14.7"
  instance_class       = "db.t3.micro"
  db_name                 = "fastapi_db"
  parameter_group_name = "default.postgres14"
  # master_username      = jsondecode("${aws_secretsmanager_secret_version.fastapi_db_credentials.secret_string}")["username"]
  # master_password      = jsondecode("${aws_secretsmanager_secret_version.fastapi_db_credentials.secret_string}")["password"]
  skip_final_snapshot  = true
  vpc_security_group_ids = [var.rds_sg]
  backup_window        = "10:00-01:00"
  backup_retention_period = 7
  auto_minor_version_upgrade = true
  depends_on = [aws_secretsmanager_secret.fastapi_db_credentials]
}

resource "aws_secretsmanager_secret" "fastapi_db_credentials" {
  name = "fastapi_db_credentials"
}

resource "aws_secretsmanager_secret_version" "fastapi_db_credentials" {
  secret_id     = aws_secretsmanager_secret.fastapi_db_credentials.id
  secret_string = "{\"username\": \"${var.fastapi_db_username}\", \"password\": \"${var.fastapi_db_password}\"}"
}


resource "aws_secretsmanager_secret" "mlflow_db_credentials" {
  name = "mlflow_db_credentials"
}

resource "aws_secretsmanager_secret_version" "mlflow_db_credentials" {
  secret_id     = aws_secretsmanager_secret.mlflow_db_credentials.id
  secret_string = "{\"username\": \"${var.mlflow_db_username}\", \"password\": \"${var.mlflow_db_password}\"}"
}
