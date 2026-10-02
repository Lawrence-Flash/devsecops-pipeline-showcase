module "platform" {
  source = "../modules/platform"

  kyverno_chart_version = var.kyverno_chart_version
  policies_dir          = abspath("${path.module}/../../../policies/kyverno")
  kubeconfig_path       = local.kubeconfig_path
}

module "app" {
  source = "../modules/app"

  namespace        = var.namespace
  chart_path       = abspath("${path.module}/../../../charts/tickets-api")
  image_repository = var.image_repository
  image_tag        = var.image_tag
  node_port        = var.node_port
  lab_api_key      = var.lab_api_key

  depends_on = [module.platform]
}
