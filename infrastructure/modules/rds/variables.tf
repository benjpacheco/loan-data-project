variable "mlflow_db_username" {
  description = "The username for the database"
}

variable "mlflow_db_password" {
  description = "The password for the database"
  sensitive   = true
}

variable "fastapi_db_username" {
  description = "Master username for the fastapi database"
  type        = string
}

variable "fastapi_db_password" {
  description = "Master password for the fastapi database"
  type        = string
  sensitive   = true
}

variable "rds_sg" {
  description = "ID of the RDS security group"
  type = any
}
