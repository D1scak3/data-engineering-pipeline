# terraform {
#   required_providers {
#     kubernetes = {
#       source  = "hashicorp/kubernetes"
#       version = "2.23.0"
#     }
#   }
# }

# provider "kubernetes" {
#   config_path = "~/.kube/config"
# }

# # namespaces
# resource "kubernetes_namespace" "cassandra" {
#   metadata {
#     annotations = {
#       name = "cassandra"
#     }

#     labels = {
#       mylabel = "label-value"
#     }

#     name = "cassandra"
#   }
# }

# resource "kubernetes_namespace" "zenprice" {
#   metadata {
#     annotations = {
#       name = "zenprice"
#     }

#     labels = {
#       mylabel = "label-value"
#     }

#     name = "zenprice"
#   }
# }

# resource "kubernetes_namespace" "strimzi-system" {
#   metadata {
#     annotations = {
#       name = "strimzi-system"
#     }

#     labels = {
#       mylabel = "label-value"
#     }

#     name = "strimzi-system"
#   }
# }

# resource "kubernetes_namespace" "monitoring" {
#   metadata {
#     annotations = {
#       name = "monitoring"
#     }

#     labels = {
#       mylabel = "label-value"
#     }

#     name = "monitoring"
#   }
# }
