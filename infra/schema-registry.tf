resource "kubernetes_service" "schema_registry" {
  metadata {
    # please do not name your service as 'schema-registry'
    # https://managing.blue/2019/10/18/port-is-deprecated-please-use-schema_registry_listeners-instead/
    name      = "schema-registry-for-avro"
    namespace = "default"
  }

  spec {
    selector = {
      app = "schema-registry"
    }

    port {
      protocol    = "TCP"
      port        = 8081
      target_port = 8081
    }
  }
}

resource "kubernetes_deployment" "schema_registry" {
  depends_on = [ helm_release.kafka ]
  metadata {
    name      = "schema-registry"
    namespace = "default"
    labels = {
      app = "schema-registry"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "schema-registry"
      }
    }

    template {
      metadata {
        labels = {
          app = "schema-registry"
        }
      }

      spec {
        container {
          name  = "schema-registry"
          image = "confluentinc/cp-schema-registry:7.9.0"

          port {
            container_port = 8081
          }

          env {
            name  = "SCHEMA_REGISTRY_HOST_NAME"
            value = "schema-registry-for-avro"
          }

          env {
            name  = "SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS"
            value = "PLAINTEXT://kafka.default.svc.cluster.local:9092"
          }

          env {
            name  = "SCHEMA_REGISTRY_LISTENERS"
            value = "http://0.0.0.0:8081"
          }
        }
      }
    }
  }
}

# resource "helm_release" "schema_registry" {
#   name       = "schema-registry"
#   repository = "https://packages.confluent.io/helm"
#   chart      = "cp-schema-registry"
#   version    = "latest"

#   set {
#     name  = "kafkastore.bootstrap.servers"
#     value = "PLAINTEXT://kafka:9092"
#   }

#   set {
#     name  = "schemaRegistry.listener"
#     value = "http://0.0.0.0:8081"
#   }
# }