variable "vpc_cidr" {
  description = "CIDR block for the VPC"
}

variable "subnet_cidr" {
  description = "CIDR block for the subnet"
}

variable "internal_cidr" {
  description = "Internal CIDR range for DB access"
  default     = "10.0.0.0/16"  
}

