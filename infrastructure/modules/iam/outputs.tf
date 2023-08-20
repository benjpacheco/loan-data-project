

output "ec2_profile_name" {
  value = aws_iam_instance_profile.ec2_profile.name
}

output "s3_rw_policy_arn" {
  value = aws_iam_role_policy.s3_rw_policy.id
}
