
output "kafka_service" {
  description = "Kafka service details"
  value       = helm_release.kafka.status
}

output "prometheus_endpoint" {
  description = "Prometheus UI endpoint"
  value       = "http://$(minikube ip):30090"
}

output "grafana_endpoint" {
  description = "Grafana dashboard endpoint"
  value       = "http://$(minikube ip):30080"
}

output "grafana_credentials" {
  description = "Default Grafana login credentials"
  value = {
    username = "admin"
    password = "admin123"  # This is set in monitoring.tf
  }
}
