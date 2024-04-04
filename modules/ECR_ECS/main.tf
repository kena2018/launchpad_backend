 terraform {  
   #required_version = ">=1.5.0"                                
   required_providers {
     aws = {
       source  = "hashicorp/aws"
       version = "~> 4.0"
     }
   }
 }
provider "aws" {
  region = "us-east-1"
  access_key = var.access_key
  secret_key = var.secret_key
  
}


resource "aws_ecr_repository" "ecr_repository" {
  name = var.ecr_repository_name
  image_tag_mutability = "IMMUTABLE"
}

# variable "ecr_repository_name" {
#   description = "name of ecr repo"
  
# }
output "ecs_repository_url" {
  value = aws_ecr_repository.ecr_repository.repository_url
}

output "ecr_repository_name" {
  value = aws_ecr_repository.ecr_repository.name
}
output "ecr_eks_repository_name" {
  value = aws_ecr_repository.ecr_repository
}
resource "aws_ecr_repository_policy" "ecr-repo-policy" {
  repository = aws_ecr_repository.ecr_repository.name
  policy     = <<EOF
  {
    "Version": "2008-10-17",
    "Statement": [
      {
        "Sid": "adds full ecr access to the ecr repository",
        "Effect": "Allow",
        "Principal": "*",
        "Action": [
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchGetImage",
          "ecr:CompleteLayerUpload",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetLifecyclePolicy",
          "ecr:InitiateLayerUpload",
          "ecr:PutImage",
          "ecr:UploadLayerPart"
        ]
      }
    ]
  }
  EOF
}