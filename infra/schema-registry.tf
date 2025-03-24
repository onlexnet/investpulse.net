resource "kubernetes_service" "schema_registry" {
  metadata {
    name      = "schema-registry-for-avro-np"
    namespace = "default"
  }

  spec {
    selector = {
      app = "schema-registry"
    }

    type = "NodePort"

    port {
      protocol    = "TCP"
      port        = 8081
      target_port = 8081
      node_port   = 30081 # Możesz zmienić na dowolny dostępny port
    }
  }
}

resource "kubernetes_service" "schema_registry_internal" {
  metadata {
    name      = "schema-registry-for-avro"
    namespace = "default"
  }

  spec {
    selector = {
      app = "schema-registry"
    }

    type = "ClusterIP"

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
            value = "PLAINTEXT://kafka-controller-headless:9092"
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
