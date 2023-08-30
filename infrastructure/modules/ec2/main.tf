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
