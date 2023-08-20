output "main_subnet" {
  value = aws_subnet.main_subnet.id
}

output "allow_http" {
  value = aws_security_group.allow_http.id
}

output "rds_sg" {
  value = aws_security_group.rds_sg.id
}