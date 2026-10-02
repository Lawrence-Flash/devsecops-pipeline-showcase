# Creates the kind cluster and loads the local image.
# The Kubernetes and Helm providers live in ../platform. They need this
# kubeconfig to exist, and Terraform cannot configure a provider from a
# cluster that has not been created yet. Apply this root first.

locals {
  kubeconfig_path = abspath("${path.module}/.kubeconfig")
}

module "cluster" {
  source = "../modules/cluster"

  cluster_name    = var.cluster_name
  kubeconfig_path = local.kubeconfig_path
  host_port       = var.host_port
  app_image       = var.app_image
}
