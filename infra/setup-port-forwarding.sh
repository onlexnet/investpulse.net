#!/bin/bash
# Script to set up port forwarding for Minikube services in a devcontainer

# Kill any existing port-forwarding processes
pkill -f "kubectl port-forward"

echo "Setting up port forwarding for Kafka brokers..."
kubectl port-forward --address 0.0.0.0 service/kafka-controller-headless 30094:9092 &
kubectl port-forward --address 0.0.0.0 service/kafka-controller-headless 30095:9092 &
kubectl port-forward --address 0.0.0.0 service/kafka-controller-headless 30096:9092 &

echo "Setting up port forwarding for Schema Registry..."
kubectl port-forward --address 0.0.0.0 service/schema-registry-for-avro-np 30081:8081 &

echo "Setting up port forwarding for Prometheus..."
kubectl port-forward -n monitoring --address 0.0.0.0 service/prometheus-kube-prometheus-prometheus 30090:9090 &

echo "Setting up port forwarding for Grafana..."
kubectl port-forward -n monitoring --address 0.0.0.0 service/prometheus-grafana 30080:80 &

echo "Setting up port forwarding for Example Web Service..."
kubectl port-forward --address 0.0.0.0 service/example-web 30999:80 &

echo "Port forwarding setup complete!"
echo "Access services at:"
echo "- Kafka: localhost:30094, localhost:30095, localhost:30096"
echo "- Schema Registry: http://localhost:30081"
echo "- Prometheus: http://localhost:30090"
echo "- Grafana: http://localhost:30080 (login: admin/admin123)"
echo "- Example Web: http://localhost:30999"

# Add the forwarded ports to your devcontainer configuration
echo "Add the following to your .devcontainer/devcontainer.json file if not already present:"
echo '"forwardPorts": [30080, 30081, 30090, 30094, 30095, 30096, 30999],'
