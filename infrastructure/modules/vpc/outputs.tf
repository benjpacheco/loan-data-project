output "main_subnet" {
  value = aws_subnet.main_subnet.id
}

output "subnet_a" {
  value = aws_subnet.subnet_a.id
}

output "subnet_c" {
  value = aws_subnet.subnet_c.id
}

output "allow_http" {
  value = aws_security_group.allow_http.id
}

output "rds_sg" {
  value = aws_security_group.rds_sg.id
}
