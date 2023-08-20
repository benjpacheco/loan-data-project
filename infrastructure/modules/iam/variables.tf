variable "bucket_name" {
  description = "Name of the bucket"
}

variable "ecr_repository_arn" {
  description = ""
}

variable "region" {
  description = "AWS Region"
}

variable "ecr_repo_name" {
    type        = string
    description = "ECR repo name"
}
