variable "ami_id" {
  description = "The AMI ID for the EC2 instance."
  type        = string
}

variable "iam_instance_profile" {
  description = "IAM instance profile name"
  type        = string
}


variable "main_subnet" {
  description = ""
}

variable "allow_http" {
  description = ""
}

variable "region" {
  description = "AWS Region"
}

variable "generated_key_name" {
  type        = string
  default     = "ben-mlops"
  description = "Key-pair generated by Terraform"
}
