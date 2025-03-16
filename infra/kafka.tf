# Available values https://github.com/bitnami/charts/blob/main/bitnami/kafka/values.yaml

resource "helm_release" "kafka" {
  name       = "kafka"
  repository = "oci://registry-1.docker.io/bitnamicharts"
  chart      = "kafka"
  version    = "31.3.0"

  set {
    name  = "controller.replicaCount"
    value = 1 # default: 3
  }

  set { 
    name = "externalAccess.enabled"
    value = "true"
  }
  set_list {
    name = "externalAccess.controller.service.externalIPs"
    value = ["192.168.49.2"] # minikube ip
  }
  set_list {
    name = "externalAccess.controller.service.nodePorts"
    value = ["30094"]
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
