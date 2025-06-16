# Available values https://github.com/bitnami/charts/blob/main/bitnami/kafka/values.yaml

provider "kubernetes" {
  config_path = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

resource "helm_release" "kafka" {
  name       = "kafka"
  repository = "oci://registry-1.docker.io/bitnamicharts"
  chart      = "kafka"
  version    = "32.2.11"
  # namespace  = kubernetes_namespace.kafka.metadata[0].name

  set {
    name  = "controller.replicaCount"
    # do not change to 1 as per
    # https://github.com/bitnami/charts/issues/16344
    value = 3
  }

  set { 
    name = "externalAccess.enabled"
    value = "true"
  }
  set_list {
    name = "externalAccess.controller.service.externalIPs"
    value = ["192.168.49.2", "192.168.49.2", "192.168.49.2"] # minikube ip
  }
  set_list {
    name = "externalAccess.controller.service.nodePorts"
    value = ["30094", "30095", "30096"]
  }

  set {
    name = "externalAccess.controller.service.type"
    value = "NodePort"
  }

  set {
    name = "listeners.client.protocol"
    value = "PLAINTEXT"
  }

  set {
    name = "listeners.external.protocol"
    value = "PLAINTEXT"
  }

  set {
    name = "advertisedListeners.client"
    value = "true"
  }
  set {
    name = "advertisedListeners.external"
    value = "true"
  }

  set {
    name = "allowPlaintextListener"
    value = "true"
  }

}

