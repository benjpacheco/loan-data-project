resource "aws_iam_role" "ec2_role" {
  name = "EC2FastAPIRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "s3_rw_policy" {
  name = "S3ReadWritePolicy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::${var.bucket_name}",
          "arn:aws:s3:::${var.bucket_name}/*"
        ],
        Effect = "Allow"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = aws_iam_role.ec2_role.name
  role = aws_iam_role.ec2_role.name
}

data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}


resource "aws_iam_role_policy" "ecr_policy" {
  name = "ECRPolicy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ],
        Resource = "arn:aws:ecr:${var.region}:${local.account_id}:repository/${var.ecr_repo_name}",
        Effect = "Allow"
      }
    ]
  })
}



resource "aws_iam_role_policy" "secrets_manager_policy" {
  name = "AccessSecretsManagerPolicy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue"
        ],
        Resource = [
          "arn:aws:secretsmanager:${var.region}:${local.account_id}:secret:fastapi_db_credentials",
          "arn:aws:secretsmanager:${var.region}:${local.account_id}:secret:mlflow_db_credentials"
        ],
        Effect = "Allow"
      }
    ]
  })
}
