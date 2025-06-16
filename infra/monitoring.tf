# Prometheus and Grafana stack for monitoring
# provider "kubernetes" {
#   config_path = var.kubeconfig_path
# }

# provider "helm" {
#   kubernetes {
#     config_path = var.kubeconfig_path
#   }
# }

# Create monitoring namespace
resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
  }
}

# Deploy Prometheus stack using Helm
resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  version    = "55.5.0"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  
  # Basic configuration values
  set {
    name  = "prometheus.service.type"
    value = "NodePort"
  }

  set {
    name  = "prometheus.service.nodePort"
    value = "30090"
  }

  # Configure the Prometheus server endpoint specifically
  set {
    name  = "prometheus.prometheusSpec.serviceMonitorSelector.matchLabels.release"
    value = "prometheus"
  }
  
  # Explicitly configure the Prometheus operator to create a NodePort service
  set {
    name  = "prometheusOperator.service.type"
    value = "NodePort"
  }
  
  # Configure the main Prometheus server service as NodePort
  set {
    name  = "prometheus.prometheusSpec.serviceType"
    value = "NodePort"
  }

  # Set specific nodePort for the Prometheus server
  set {
    name  = "prometheus.prometheusSpec.service.nodePort"
    value = "30090"
  }

  set {
    name  = "grafana.service.type"
    value = "NodePort"
  }

  set {
    name  = "grafana.service.nodePort"
    value = "30080"
  }

  # Default admin user for Grafana
  set {
    name  = "grafana.adminPassword"
    value = "admin123"  # Change this in production
  }

  # Enable persistent storage for Prometheus
  set {
    name  = "prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.accessModes[0]"
    value = "ReadWriteOnce"
  }

  set {
    name  = "prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage"
    value = "5Gi"
  }

  # Add Kafka-specific scrape configs
  set {
    name  = "prometheus.prometheusSpec.additionalScrapeConfigs[0].job_name"
    value = "kafka"
  }

  set {
    name  = "prometheus.prometheusSpec.additionalScrapeConfigs[0].static_configs[0].targets[0]"
    value = "kafka-controller-headless:9092"
  }

  set {
    name  = "prometheus.prometheusSpec.additionalScrapeConfigs[0].metrics_path"
    value = "/metrics"
  }

  # Add Schema Registry scrape config
  set {
    name  = "prometheus.prometheusSpec.additionalScrapeConfigs[1].job_name"
    value = "schema-registry"
  }

  set {
    name  = "prometheus.prometheusSpec.additionalScrapeConfigs[1].static_configs[0].targets[0]"
    value = "schema-registry-for-avro:8081"
  }

  set {
    name  = "prometheus.prometheusSpec.additionalScrapeConfigs[1].metrics_path"
    value = "/metrics"
  }

  # Make Prometheus and Grafana available for external components
  set {
    name  = "prometheus.service.externalTrafficPolicy"
    value = "Local"
  }

  set {
    name  = "grafana.service.externalTrafficPolicy"
    value = "Local"
  }

  # Configure retention period for Prometheus data
  set {
    name  = "prometheus.prometheusSpec.retention"
    value = "24h"  # Adjust based on your needs and available storage
  }
}

# Deploy Kafka Exporter for better Kafka metrics
resource "helm_release" "kafka_exporter" {
  name       = "kafka-exporter"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "prometheus-kafka-exporter"
  version    = "2.0.0"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  depends_on = [helm_release.prometheus]

  # Kafka server needs to be provided as a list
  set_list {
    name  = "kafkaServer"
    value = ["kafka-controller-headless:9092"]
  }

  set {
    name  = "service.type"
    value = "ClusterIP"
  }
}
