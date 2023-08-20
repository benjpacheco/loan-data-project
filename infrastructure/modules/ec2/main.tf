resource "aws_instance" "fastapi_app" {
  ami           = var.ami_id
  instance_type = "t3a.xlarge"
  key_name      = aws_key_pair.generated_key.key_name
  
  subnet_id = var.main_subnet
  vpc_security_group_ids = [var.allow_http]

  iam_instance_profile = var.iam_instance_profile


  tags = {
    Name = "FastAPI-App"
  }
  user_data = <<-EOT
         #!/bin/bash
         sudo yum update -y
         sudo yum install -y docker
         sudo service docker start
         sudo usermod -a -G docker ec2-user
      
EOT

}

resource "tls_private_key" "private_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = var.generated_key_name
  public_key = tls_private_key.private_key.public_key_openssh
}



 #  # Get MLflow database credentials
        #  # Retrieve secret values
        #  mlflow_db_credentials=$(aws secretsmanager get-secret-value --secret-id ${data.aws_secretsmanager_secret_version.mlflow_db_credentials} --query SecretString --output text)
        #  # Parse the secret values using jq or other tools
        #  mlflow_db_username=$(echo $mlflow_db_credentials | jq -r '.username')
        #  mlflow_db_password=$(echo $mlflow_db_credentials | jq -r '.password')

        #  # Placeholder for ECR URL, Replace this with your actual ECR URL
        #  ECR_URL="<account-id>.dkr.ecr.<region>.amazonaws.com/<repository-name>"

        #  # Login to ECR
        #  aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin $ECR_URL

        #  # Pull the Docker image and run
        #  docker pull $ECR_URL

        #  docker-compose up -d

# data "aws_secretsmanager_secret" "mlflow_db_credentials" {
#   name = "mlflow_db_credentials"
# }

# data "aws_secretsmanager_secret_version" "mlflow_db_credentials" {
#   secret_id     = data.aws_secretsmanager_secret.mlflow_db_credentials.arn
# }


