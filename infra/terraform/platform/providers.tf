# Point these providers at the kubeconfig the cluster root already wrote.
# `terraform validate` does not connect. `terraform plan` needs the cluster up.

locals {
  kubeconfig_path = abspath("${path.module}/../cluster/.kubeconfig")
}

provider "kubernetes" {
  config_path = local.kubeconfig_path
}

provider "helm" {
  kubernetes = {
    config_path = local.kubeconfig_path
  }
}
