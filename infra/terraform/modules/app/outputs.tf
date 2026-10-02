output "namespace" {
  value = kubernetes_namespace_v1.tickets.metadata[0].name
}
