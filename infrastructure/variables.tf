variable "region" {
  description = "AWS Region"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR block for the subnet"
  default     = "10.0.1.0/24"
}

variable "ami_id" {
  description = "AMI ID for EC2 instance"
}

variable "project_id" {
  description = "project_id"
  default     = "loan-data-project"
}

variable "mlflow_db_username" {
  description = "Username for the MLFlow database"
  type        = string
}

variable "mlflow_db_password" {
  description = "Password for the MLFlow database"
  type        = string
}

variable "fastapi_db_username" {
  description = "Username for the FastAPI database"
  type        = string
}

variable "fastapi_db_password" {
  description = "Password for the FastAPI database"
  type        = string
}

variable "ecr_repo_name" {
  description = ""
  default     = "fastapi_app_bp"
}

variable "bucket_name" {
  description = "Name of the bucket"
}

