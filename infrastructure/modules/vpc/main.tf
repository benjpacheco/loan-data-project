resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr

  tags = {
    Name = "Main VPC"
  }
}

resource "aws_subnet" "main_subnet" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.subnet_cidr
  availability_zone = "us-east-2b"
  map_public_ip_on_launch = true

  tags = {
    Name = "Main Subnet"
  }
}

resource "aws_subnet" "subnet_a" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.subnet_a_cidr
  availability_zone = "us-east-2a"
  map_public_ip_on_launch = true

  tags = {
    Name = "Main Subnet"
  }
}

resource "aws_subnet" "subnet_c" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.subnet_c_cidr
  availability_zone = "us-east-2c"
  map_public_ip_on_launch = true

  tags = {
    Name = "Main Subnet"
  }
}

resource "aws_security_group" "allow_http" {
  name        = "allow_http"
  description = "Allow HTTP inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group_rule" "ec2_to_rds" {
  security_group_id = aws_security_group.allow_http.id
  type              = "egress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  source_security_group_id = aws_security_group.rds_sg.id
}

resource "aws_security_group" "rds_sg" {
  name        = "rds_sg"
  description = "Allow internal traffic for RDS"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.internal_cidr]
  }
}
