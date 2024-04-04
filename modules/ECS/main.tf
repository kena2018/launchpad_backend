terraform {  
 # required_version = ">=1.5.0"                                
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

#  terraform {
#         backend "local" {
#         path = "ecs.tfstate"
#        }
#        }
provider "aws" {
  region = var.region
  access_key = var.access_key
  secret_key = var.secret_key
  
}

resource "aws_ecs_cluster" "ecs_cluster" {
  name = var.cluster_name
}


resource "aws_ecs_task_definition" "ecs_task_definition" {
  family                   = var.task_family
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  task_role_arn = aws_iam_role.ecs_task_role.arn

  cpu        = var.cpu
  memory     = var.memory
 # task_role_arn = var.task_role_arn

  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = var.container_name
       image = var.container_image
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "ecs_service" {
  name            = var.service_name
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.ecs_task_definition.family
  launch_type     = "FARGATE"
  desired_count   = var.desired_count

  network_configuration {
    subnets = [aws_subnet.private_subnet.id, aws_subnet.public_subnet.id]
    assign_public_ip = true
    security_groups = [aws_security_group.ecs_security_group.id]
  }
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs_task_execution_role"

  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
          "Service": "ecs-tasks.amazonaws.com"
        }
      }
    ]
  }
  EOF
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  role       = aws_iam_role.ecs_task_execution_role.name
}

resource "aws_iam_role" "ecs_task_role" {
  name = "ecs-task-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "ecs_task_role_attachment" {
  name       = "ecs-task-policy-attachment"
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess" 
  roles      = [aws_iam_role.ecs_task_role.name]
}

resource "aws_vpc" "ecs_vpc" {
  cidr_block = var.vpc_cidr_block
  enable_dns_support = true
  enable_dns_hostnames = true
  tags = {
    Name = "ecs-vpc"
  }
}

resource "aws_subnet" "private_subnet" {
  vpc_id     = aws_vpc.ecs_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true  
  tags = {
    Name = "ecs-subnet"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id     = aws_vpc.ecs_vpc.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = true  
  tags = {
    Name = "ecs-subnet"
  }
}

 resource "aws_security_group" "ecs_security_group" {
  vpc_id = aws_vpc.ecs_vpc.id

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
    Name = "ecs-security-group"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.ecs_vpc.id
}


resource "aws_route_table" "public_subnet" {
  vpc_id = aws_vpc.ecs_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "subnet_a_association" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_subnet.id
}