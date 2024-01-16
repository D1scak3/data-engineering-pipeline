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
  cpus         = 8
  memory       = 8192
  addons = [
    "default-storageclass",
    "storage-provisioner",
    "metallb",
    "metrics-server"
  ]
}

provider "kubernetes" {
  host = minikube_cluster.docker.host

  client_certificate     = minikube_cluster.docker.client_certificate
  client_key             = minikube_cluster.docker.client_key
  cluster_ca_certificate = minikube_cluster.docker.cluster_ca_certificate
}

resource "kubernetes_namespace" "strimzi" {
  metadata {
    annotations = {
      name = "strimzi"
    }

    labels = {
      mylabel = "strimzi"
    }

    name = "strimzi"
  }
}

resource "kubernetes_namespace" "zenprice" {
  metadata {
    annotations = {
      name = "zenprice"
    }

    labels = {
      mylabel = "zenprice"
    }

    name = "zenprice"
  }
}

resource "kubernetes_namespace" "monitoring" {
  metadata {
    annotations = {
      name = "monitoring"
    }

    labels = {
      mylabel = "monitoring"
    }

    name = "monitoring"
  }
}
