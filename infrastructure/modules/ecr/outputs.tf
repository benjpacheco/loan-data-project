
output "arn" {
value = aws_ecr_repository.fastapi_app.arn
}


output "repository_url" {
value = aws_ecr_repository.fastapi_app.repository_url
}
