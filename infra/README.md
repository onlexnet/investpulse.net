# Predictive Trading Infrastructure

This repository contains Terraform configuration for deploying a local Apache Kafka infrastructure on Minikube, designed for predictive trading applications. The infrastructure includes Kafka brokers, a Schema Registry for managing Avro schemas, and a Prometheus monitoring stack.

## Architecture Overview

The architecture consists of the following components:

### 1. Apache Kafka Cluster
- **Implementation**: Deployed using the Bitnami Helm chart
- **Configuration**:
  - 3 Kafka controller nodes for high availability
  - External access enabled via NodePort services
  - PLAINTEXT protocol for both internal and external listeners
  - NodePorts: 30094, 30095, 30096 for external access
  - IP: 192.168.49.2 (Minikube IP)

### 2. Schema Registry
- **Implementation**: Confluent Schema Registry (Docker image: confluentinc/cp-schema-registry:7.9.0)
- **Configuration**:
  - Single replica deployment
  - Accessible internally via ClusterIP service named `schema-registry-for-avro`
  - Externally accessible via NodePort service on port 30081
  - Connected to Kafka bootstrap servers at `kafka-controller-headless:9092`

### 3. Prometheus Monitoring Stack
- **Implementation**: Deployed using the kube-prometheus-stack Helm chart
- **Configuration**:
  - Prometheus server for metrics collection and storage
  - Grafana for metrics visualization
  - NodePort services for external access
  - Kafka metrics collection via Kafka Exporter
  - NodePorts: 30090 (Prometheus), 30080 (Grafana)
  - Default Grafana credentials: admin/admin123

### 4. Example Web Service
- **Implementation**: Simple Nginx-based web server
- **Purpose**: Test service to verify NodePort connectivity
- **Configuration**:
  - Single replica deployment
  - Custom HTML content via ConfigMap
  - Accessible externally via NodePort 30999

### 5. Infrastructure Diagram

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                              Minikube Cluster                                  │
│                                                                                │
│  ┌─────────────────┐   ┌───────────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │   Kafka Cluster │   │  Schema Registry  │  │  Prometheus  │  │  Example  │  │
│  │   (3 Brokers)   │◄─►│                   │  │    Stack     │  │    Web    │  │
│  └────────┬────────┘   └─────────┬─────────┘  └──────┬───────┘  └─────┬─────┘  │
│           │                      │                   │                │        │
└───────────┼──────────────────────┼───────────────────┼────────────────┼────────┘
            │                      │                   │                │
            ▼                      ▼                   ▼                ▼
     External Access        External Access     External Access  External Access
     NodePorts:             NodePort:           NodePorts:       NodePort:
     30094, 30095, 30096    30081               30090, 30080     30999
                                               (Prometheus, Grafana)
```

## Getting Started

### Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/) - For local Kubernetes cluster
- [Terraform](https://www.terraform.io/downloads.html) - For infrastructure as code
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) - For Kubernetes CLI
- [Helm](https://helm.sh/docs/intro/install/) - For chart deployments

### Quick Start

1. Start the Minikube cluster:
   ```bash
   minikube start
   ```

2. Apply the Terraform configuration:
   ```bash
   terraform init
   terraform apply
   ```

3. Access the services:

   #### For Direct Minikube Access (Outside Devcontainer)
   
   Get the Minikube IP address:
   ```bash
   minikube ip
   ```
   
   Then access services using the Minikube IP and NodePorts:
   - Kafka: `<minikube-ip>:30094,<minikube-ip>:30095,<minikube-ip>:30096`
   - Schema Registry: `http://<minikube-ip>:30081`
   - Prometheus: `http://<minikube-ip>:30090`
   - Grafana: `http://<minikube-ip>:30080`
   - Example Web Service: `http://<minikube-ip>:30999`
   
   #### For Devcontainer Setup
   
   When running inside a devcontainer, NodePorts are not directly accessible. Use the provided script to set up port forwarding:
   
   ```bash
   ./setup-port-forwarding.sh
   ```
   
   This script forwards the necessary ports to make the services accessible locally:
   
   - Kafka: `localhost:30094,localhost:30095,localhost:30096`
   - Schema Registry: `http://localhost:30081`
   - Prometheus: `http://localhost:30090`
   - Grafana: `http://localhost:30080`
   - Example Web Service: `http://localhost:30999`
   
   Make sure your devcontainer configuration includes these forwarded ports:
   ```json
   "forwardPorts": [30080, 30081, 30090, 30094, 30095, 30096, 30999]
   ```

## Configuration Options

### Variables

- `kubeconfig_path`: Path to the kubeconfig file (default: `~/.kube/config`)

### State Management

Terraform state is stored locally within the image. The entire infrastructure exists as long as the Minikube cluster is running.

## Components Details

### Kafka Configuration

The Kafka deployment uses the Bitnami Kafka Helm chart with customized settings:
- Version: 32.2.11
- External access enabled via NodePort services
- PLAINTEXT protocol for simplicity (Note: Not recommended for production)

### Schema Registry Configuration

The Schema Registry provides a RESTful interface for storing and retrieving Avro schemas:
- Connects to the Kafka cluster for schema storage
- Exposes HTTP API for schema management
- Accessible both internally within the cluster and externally

### Monitoring Configuration

The monitoring stack uses Prometheus and Grafana:

#### Prometheus
- Deployed from the kube-prometheus-stack Helm chart
- Configured to scrape metrics from Kafka and Schema Registry
- Persistent storage enabled with 5Gi storage
- 24-hour data retention period
- Accessible externally via NodePort 30090

#### Grafana
- Included in the kube-prometheus-stack
- Pre-configured dashboards for Kubernetes and Kafka monitoring
- Default credentials: admin/admin123 (change this for production)
- Accessible externally via NodePort 30080

#### Kafka Exporter
- Dedicated exporter for Kafka metrics
- Exports metrics in Prometheus format
- Monitors Kafka broker health, consumer groups, and topic metrics

## Development Use Cases

This infrastructure is designed for:
1. Developing and testing predictive trading algorithms
2. Working with event-driven architectures
3. Processing real-time market data streams
4. Testing schema evolution with Avro

## Notes

- This setup is intended for local development only and is not production-ready
- Security features are minimal for development simplicity
- For production use, consider enabling authentication and encryption

