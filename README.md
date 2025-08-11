# investpulse.net

## Decisions
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
- Install local services using terraform in infra subdir