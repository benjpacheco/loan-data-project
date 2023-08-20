output "ec2_instance_public_ip" {
  description = "Public IP address of the EC2 instance."
  value       = aws_instance.fastapi_app.public_ip
}

output "ec2_instance_private_key_path" {
  value = tls_private_key.private_key.private_key_pem
}

output "public_key_openssh" {
  value = tls_private_key.private_key.public_key_openssh
}
