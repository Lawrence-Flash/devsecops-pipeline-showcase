resource "kubernetes_namespace_v1" "tickets" {
  metadata {
    name = var.namespace
    labels = {
      "pod-security.kubernetes.io/enforce" = "restricted"
      "pod-security.kubernetes.io/audit"   = "restricted"
      "pod-security.kubernetes.io/warn"    = "restricted"
    }
  }
}

resource "helm_release" "tickets" {
  name            = "tickets-api"
  chart           = var.chart_path
  namespace       = kubernetes_namespace_v1.tickets.metadata[0].name
  wait            = true
  timeout         = 900
  atomic          = true
  cleanup_on_fail = true

  values = [
    yamlencode({
      image = {
        repository = var.image_repository
        tag        = var.image_tag
        pullPolicy = "IfNotPresent"
      }
      service = {
        type     = "NodePort"
        port     = 8000
        nodePort = var.node_port
      }
      labApiKey = var.lab_api_key
    })
  ]
}
