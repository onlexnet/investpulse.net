# predictivetrading.net

## Decisions
- use [DAPR multi-app run](https://docs.dapr.io/developing-applications/local-development/multi-app-dapr-run/multi-app-overview/)
- use [devcontainers/vscode](https://containers.dev/guide/dockerfile) as main dev tool

## Hints

- run minikube
  - if error *... failed to get current CoreDNS ...*
    ```
    minikube status: 
    minikube
    type: Control Plane
    host: Running
    kubelet: Running
    apiserver: Stopped
    kubeconfig: Configured
    ```
  - try to fix
    ```
    minikube stop
    minikube delete
    minikube start
    ```
- [Install Kafka using Helm](https://bitnami.com/stack/kafka/helm)