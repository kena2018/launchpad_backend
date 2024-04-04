variable "region" {
  description = "AWS region"
}

variable "ami" {
  description = "AMI ID for the EC2 instance"
}

variable "instance_type" {
  description = "Instance type for the EC2 instance"
}

variable "instance_name" {
  description = "Name tag for the EC2 instance"
}

# variable "subnet_id" {
#   description = "Subnet ID"
# }

 variable "key_name" {
  description = "name of the keyname"
   
 }
 
# variable "security_group" {
#   description = "Security Group"
#   type        = list(any)
# }

variable "access_key" {
  description = "enter access-key"
  
}

variable "secret_key" {
  description = "enter secret-key"
  
}