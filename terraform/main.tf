terraform {
  required_providers {
    minikube = {
      source  = "scott-the-programmer/minikube"
      version = "0.3.6"
    }
  }
}

provider "minikube" {
  kubernetes_version = "v1.28.3"
}

resource "minikube_cluster" "docker" {
  driver       = "docker"
  cluster_name = "data-pipeline"
  addons = [
    "default-storageclass",
    "storage-provisioner",
    "metallb",
    "metrics-server"
  ]
}
