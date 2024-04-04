variable "access_key" {
  description = "enter access-key"
  
}

variable "secret_key" {
  description = "enter secret-key"
  
}

variable "region" {
  description = "AWS region"
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
}

variable "node_group_name" {
  description = "Name of node group"
  
}

variable "desired_size" {
  description = "Desired number of nodes "
  default     = "1"
}

variable "vpc_cidr_block" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}
