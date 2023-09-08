output "ec2_instance_public_ip" {
  description = "Public IP address of the EC2 instance."
  value       = module.ec2.ec2_instance_public_ip
}

output "ec2_instance_private_key_path" {
  value     = module.ec2.ec2_instance_private_key_path
  sensitive = true
}


output "repository_url" {
  value = module.ecr.repository_url
}
output "arn" {
  value = module.ecr.arn
}


output "mlflow_db_endpoint" {
  value = module.rds.mlflow_db_endpoint
}


output "mlflow_database_credentials" {
  value = jsonencode({
    username = module.rds.mlflow_database_credentials.username,
    password = module.rds.mlflow_database_credentials.password
  })
  sensitive = true
}


output "mlflow_database_name" {
  value = module.rds.mlflow_database_name
}

output "s3_bucket_name" {
  value = module.s3_bucket.s3_bucket_name
}
