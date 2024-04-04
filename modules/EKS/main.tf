terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      #version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region     = var.region # change your region
  access_key = var.access_key
  secret_key = var.secret_key
}

# Create VPC for EKS
resource "aws_vpc" "eks_vpc" {
  cidr_block           = var.vpc_cidr_block # Adjust the CIDR block as needed
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "eks-vpc"
  }
}

resource "aws_security_group" "eks_security_group" {
  vpc_id = aws_vpc.eks_vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "eks-security-group"
  }
}

# Create public subnets for EKS
resource "aws_subnet" "eks_public_subnet_1" {
  vpc_id                  = aws_vpc.eks_vpc.id
  cidr_block              = "10.0.1.0/24" # Adjust the CIDR block as needed
  availability_zone       = "${var.region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "eks-public-subnet-1"
  }
}

resource "aws_subnet" "eks_public_subnet_2" {
  vpc_id                  = aws_vpc.eks_vpc.id
  cidr_block              = "10.0.2.0/24" # Adjust the CIDR block as needed
  availability_zone       = "${var.region}b"
  map_public_ip_on_launch = true

  tags = {
    Name = "eks-public-subnet-2"
  }
}

# Internet Gateway for public subnets
resource "aws_internet_gateway" "eks_igw" {
  vpc_id = aws_vpc.eks_vpc.id
}

# Route table for public subnets
resource "aws_route_table" "eks_public_subnet_1" {
  vpc_id = aws_vpc.eks_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.eks_igw.id
  }
}

resource "aws_route_table" "eks_public_subnet_2" {
  vpc_id = aws_vpc.eks_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.eks_igw.id
  }
}

# Associate public subnets with public route tables
resource "aws_route_table_association" "eks_public_subnet_1_association" {
  subnet_id      = aws_subnet.eks_public_subnet_1.id
  route_table_id = aws_route_table.eks_public_subnet_1.id
}

resource "aws_route_table_association" "eks_public_subnet_2_association" {
  subnet_id      = aws_subnet.eks_public_subnet_2.id
  route_table_id = aws_route_table.eks_public_subnet_2.id
}

# IAM Role for EKS cluster
resource "aws_iam_role" "eks_cluster" {
  name = "eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "eks_cluster_policy" {
  name       = "eks-cluster-policy"
  roles      = [aws_iam_role.eks_cluster.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

# EKS Cluster
resource "aws_eks_cluster" "eks" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids = [
      aws_subnet.eks_public_subnet_1.id,
      aws_subnet.eks_public_subnet_2.id,
    ]
  }
}

# IAM Role for EKS worker nodes
resource "aws_iam_role" "eks_node_group" {
  name = var.node_group_name

  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
    Version = "2012-10-17"
  })
}

#ESI Driver Policy 
resource "aws_iam_policy" "ebs_permissions_policy" {
  name        = "EBSPermissionsPolicy"
  description = "Policy allowing EC2 actions"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "ec2:AttachVolume",
          "ec2:CreateSnapshot",
          "ec2:CreateTags",
          "ec2:CreateVolume",
          "ec2:DeleteSnapshot",
          "ec2:DeleteTags",
          "ec2:DeleteVolume",
          "ec2:DescribeInstances",
          "ec2:DescribeSnapshots",
          "ec2:DescribeTags",
          "ec2:DescribeVolumes",
          "ec2:DetachVolume"
        ],
        "Resource" : "*"
      }
    ]
  })
}

# ESI Driver Policy Role policy attachments for EKS worker nodes
resource "aws_iam_policy_attachment" "eks_node_group_ebs_node_policy" {
  name       = "attach-policy-to-user"
  policy_arn = aws_iam_policy.ebs_permissions_policy.arn
  roles       = [aws_iam_role.eks_node_group.name]
}


# IAM Role policy attachments for EKS worker nodes
resource "aws_iam_role_policy_attachment" "eks_node_group_eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_group.name
}

resource "aws_iam_role_policy_attachment" "eks_node_group_eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_group.name
}

resource "aws_iam_role_policy_attachment" "eks_node_group_ecr_readonly_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_group.name
}

# Managed Node Group for EKS
resource "aws_eks_node_group" "eks" {
  cluster_name    = aws_eks_cluster.eks.name
  node_group_name = var.node_group_name
  node_role_arn   = aws_iam_role.eks_node_group.arn

  subnet_ids = [
    aws_subnet.eks_public_subnet_1.id,
    aws_subnet.eks_public_subnet_2.id,
  ]
  scaling_config {
    desired_size = 1
    max_size     = 2 #Q.Ask the user input as MAX & MIN=1? DESIRED = MIN?
    min_size     = 1
  }
  instance_types = ["t3.medium"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_node_group_eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_node_group_eks_cni_policy,
    aws_iam_role_policy_attachment.eks_node_group_ecr_readonly_policy,
    aws_eks_cluster.eks
  ]
}