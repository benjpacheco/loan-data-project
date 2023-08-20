resource "aws_ecr_repository" "fastapi_app" {
  name                 = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"
}
