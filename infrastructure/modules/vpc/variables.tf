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

variable "subnet_a_cidr" {
  description = "CIDR block for the main subnet"
  default     = "10.0.20.0/24"
}

variable "subnet_c_cidr" {
  description = "CIDR block for the main subnet"
  default     = "10.0.30.0/24"
}
