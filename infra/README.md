# Kafka on Minikube with Terraform
This Terraform configuration sets up a local Minikube cluster and deploys Kafka using Helm.

## Quick start
- run minikube
- terraform apply

## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Terraform](https://www.terraform.io/downloads.html)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Helm](https://helm.sh/docs/intro/install/)

## Variables

- `kubeconfig_path`: Path to the kubeconfig file (default: `~/.kube/config`)

## Outputs

- `kafka_service`: Kafka service details
```
```
Local place to install everything on local minikube cluster. Terraform state is kept in the image, as the whole infra exists as long as the image is rebuild

