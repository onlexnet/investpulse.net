# Namespace dla monitoring
resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
  }
}

# OpenTelemetry Collector
resource "helm_release" "otel_collector" {
  name       = "otel-collector"
  repository = "https://open-telemetry.github.io/opentelemetry-helm-charts"
  chart      = "opentelemetry-collector"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name

  set {
    name  = "mode"
    value = "deployment"
  }

  set {
    name  = "service.type"
    value = "NodePort"
  }

  set {
    name = "image.repository"
    value = "otel/opentelemetry-collector-k8s"
  }
}

# Instalacja Prometheusa
resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "prometheus"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name

  set {
    name  = "server.service.type"
    value = "ClusterIP"
  }
}


# Instalacja Grafany z ustawieniem basePath na /grafana
resource "helm_release" "grafana" {
  name       = "grafana"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "grafana"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name

  set {
    name  = "service.type"
    value = "ClusterIP"
  }

  set {
    name  = "adminPassword"
    value = "admin"
  }

  # Ustawienie basePath na /grafana
  set {
    name  = "grafana.ini.server.root_url"
    value = "http://grafana.local/grafana/"
  }

  set {
    name  = "grafana.ini.server.serve_from_sub_path"
    value = "true"
  }
}

# Ingress dla Prometheusa
resource "kubernetes_ingress_v1" "prometheus" {
  metadata {
    name      = "prometheus-ingress"
    namespace = kubernetes_namespace.monitoring.metadata[0].name
    annotations = {
      "nginx.ingress.kubernetes.io/rewrite-target" = "/"
    }
  }

  spec {
    ingress_class_name = "nginx"

    rule {
      host = "prometheus.local"
      http {
        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = "prometheus-server"
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}

# Ingress dla Grafany (z poprzedniej konfiguracji)
resource "kubernetes_ingress_v1" "grafana" {
  metadata {
    name      = "grafana-ingress"
    namespace = kubernetes_namespace.monitoring.metadata[0].name
    annotations = {
      "nginx.ingress.kubernetes.io/rewrite-target" = "/$1"
    }
  }

  spec {
    ingress_class_name = "nginx"

    rule {
      host = "grafana.local"
      http {
        path {
          path      = "/grafana(/|$)(.*)"
          path_type = "Prefix"

          backend {
            service {
              name = "grafana"
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}

output "grafana_url" {
  value = "http://grafana.local/grafana"
}

output "prometheus_url" {
  value = "http://prometheus.local"
}