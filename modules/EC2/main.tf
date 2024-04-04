
terraform {  
  required_version = ">=1.5.0"                                
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}
provider "aws" {
  region = var.region
  access_key = var.access_key
  secret_key = var.secret_key
  
}
#  terraform {
#   backend "local" {
#   path = "ec2.tfstate"
#   }
#   }
resource "aws_instance" "instance" {
  ami           = var.ami
  instance_type = var.instance_type
  subnet_id              = "subnet-0238aaff4984b2e9b"
 # vpc_security_group_ids = var.security_group

  tags = {
    Name = var.instance_name
  }
}

resource "aws_vpc" "my_vpc" {
  cidr_block = "10.0.0.0/16" 
}

resource "aws_ebs_volume" "my_volume" {
  availability_zone = "us-east-1a"  
  size              = 8  # Replace with the desired size in GB        
}


 resource "aws_key_pair" "key-pair" {
 key_name = var.key_name
 public_key = tls_private_key.rsa.public_key_openssh
}
resource "tls_private_key" "rsa" {
algorithm = "RSA"
rsa_bits  = 4096
}
resource "local_file" "tf-key" {
content  = tls_private_key.rsa.private_key_pem
filename = var.key_name
file_permission = 0600
}

