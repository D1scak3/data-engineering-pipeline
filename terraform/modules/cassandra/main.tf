# provider "kubernetes" {
#   host = minikube_cluster.docker.host

#   client_certificate     = minikube_cluster.docker.client_certificate
#   client_key             = minikube_cluster.docker.client_key
#   cluster_ca_certificate = minikube_cluster.docker.cluster_ca_certificate
# }

provider "kubernetes" {
  config_path = "~/.kube/config"  # Path to your kubeconfig file, adjust as needed
}

resource "kubernetes_namespace" "cassandra" {
  metadata {
    annotations = {
      name = "cassandra"
    }

    labels = {
      mylabel = "cassandra"
    }

    name = "cassandra"
  }
}

resource "kubernetes_service" "cassandra" {
  metadata {
    name = "cassandra"
    labels = {
      app = "cassandra"
    }
  }

  spec {
    cluster_ip = "None"
    port {
      port        = 9042
      target_port = "cassandra"
    }
    selector = {
      app = "cassandra"
    }
  }
}

resource "kubernetes_service" "cassandra_metrics" {
  metadata {
    name = "cassandra-metrics"
    labels = {
      tag = "cassandra-metrics"
    }
  }

  spec {
    cluster_ip = "None"
    port {
      port        = 7070
      target_port = "cassandra-metrics"
    }
    selector = {
      tag = "cassandra-metrics"
    }
  }
}

resource "kubernetes_stateful_set" "cassandra" {
  metadata {
    name = "cassandra"
    labels = {
      app = "cassandra"
    }
  }

  spec {
    service_name = kubernetes_service.cassandra.metadata[0].name
    replicas     = 3

    selector {
      match_labels = {
        app = "cassandra"
      }
    }

    template {
      metadata {
        labels = {
          app = "cassandra"
          tag = "cassandra-metrics"
        }
      }

      spec {
        termination_grace_period_seconds = 1800

        volume {
          name = "cassandra-vol"
          persistent_volume_claim {
            claim_name = "cassandra-pvc"
          }
        }

        container {
          name  = "cassandra"
          image = "d1scak3/cassandra:4.0_config"

          port {
            container_port = 7000
            name           = "intra-node"
          }
          port {
            container_port = 7001
            name           = "tls-intra-node"
          }
          port {
            container_port = 7070
            name           = "metrics"
          }
          port {
            container_port = 7199
            name           = "jmx"
          }
          port {
            container_port = 9042
            name           = "cql"
          }

          resources {
            limits = {
              cpu    = "1024m"
              memory = "2Gi"
            }
            requests = {
              cpu    = "512m"
              memory = "1Gi"
            }
          }

          security_context {
            capabilities {
              add = ["IPC_LOCK"]
            }
          }

          lifecycle {
            pre_stop {
              exec {
                command = ["/bin/sh", "-c", "nodetool drain"]
              }
            }
          }

          env {
            name  = "MAX_HEAP_SIZE"
            value = "512M"
          }
          env {
            name  = "HEAP_NEWSIZE"
            value = "100M"
          }
          env {
            name  = "CASSANDRA_SEEDS"
            value = "cassandra-0.cassandra.cassandra.svc.cluster.local"
          }
          env {
            name  = "CASSANDRA_ENDPOINT_SNITCH"
            value = "GossipingPropertyFileSnitch"
          }
          env {
            name  = "CASSANDRA_CLUSTER_NAME"
            value = "zenprice"
          }
          env {
            name  = "CASSANDRA_DC"
            value = "dc1"
          }
          env {
            name  = "CASSANDRA_RACK"
            value = "rack1"
          }
          env {
            name = "POD_IP"
            value_from {
              field_ref {
                field_path = "status.podIP"
              }
            }
          }

          volume_mount {
            name      = "cassandra-vol"
            mount_path = "/cassandra_data"
          }
        }
      }
    }
  }
}