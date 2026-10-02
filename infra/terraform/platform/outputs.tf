output "namespace" {
  value = module.app.namespace
}

output "url" {
  value = "http://127.0.0.1:${var.node_port}"
}
