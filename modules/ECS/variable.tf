variable "region" {
  description = "AWS region"
}

variable "cluster_name" {
  description = "Name of the ECS cluster"

}


variable "container_image" {
  description = "Docker image for the container"
}
variable "access_key" {
  description = "enter access-key"
  
}

variable "secret_key" {
  description = "enter secret-key"
  
}

variable "task_family" {
  description = "Family name of the ECS task definition"
}

variable "cpu" {
  description = "CPU units for the ECS task"
  default     = 256
}

variable "memory" {
  description = "Memory for the ECS task"
  default     = 512
}

# variable "task_role_arn" {
#   description = "ARN of the IAM role to be used by the ECS task"
# }

variable "container_name" {
  description = "Name of the container within the task"
}



variable "container_port" {
  description = "Port on which the container listens"
}

variable "host_port" {
  description = "Port on the host to which container port is mapped"
}

variable "service_name" {
  description = "Name of the ECS service"
}

variable "desired_count" {
  description = "Number of tasks to run in the service"
}


variable "vpc_cidr_block" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

