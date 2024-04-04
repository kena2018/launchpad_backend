output "eks_cluster_name" {
  value = aws_eks_cluster.eks.name
}

output "node_group_name" {
  value = var.node_group_name
}

# output "node_group_name" {
#   value = aws_eks_node_group.eks.node_group_name.name
# }

# output "eks_cluster_id" {
#   value = aws_eks_cluster.devops-eks.id
# }
