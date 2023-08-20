terraform {
  backend "s3" {
    bucket  = "mlops-project-state-bucket-bp"
    key     = "mlops-project.tfstate"
    encrypt = true
    region = "us-east-2"
  }
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

module "vpc" {
  source      = "./modules/vpc"
  vpc_cidr    = var.vpc_cidr
  subnet_cidr = var.subnet_cidr
}

module "s3_bucket" {
  source      = "./modules/s3"
  bucket_name = var.bucket_name
}

module "ecr" {
  source        = "./modules/ecr"
  ecr_repo_name = var.ecr_repo_name
}

module "iam" {
  source             = "./modules/iam"
  bucket_name        = module.s3_bucket.s3_bucket_name
  ecr_repository_arn = module.ecr.arn
  region             = var.region
  ecr_repo_name      = var.ecr_repo_name
}

module "ec2" {
  source               = "./modules/ec2"
  region               = var.region
  ami_id               = var.ami_id
  main_subnet          = module.vpc.main_subnet
  mlflow_db_username   = var.mlflow_db_username
  mlflow_db_password   = var.mlflow_db_password
  iam_instance_profile = module.iam.ec2_profile_name
  allow_http           = module.vpc.allow_http
}

module "rds" {
  source              = "./modules/rds"
  mlflow_db_username  = var.mlflow_db_username
  mlflow_db_password  = var.mlflow_db_password
  fastapi_db_username = var.fastapi_db_username
  fastapi_db_password = var.fastapi_db_password
  rds_sg              = module.vpc.rds_sg
}

