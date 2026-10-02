resource "helm_release" "kyverno" {
  name             = "kyverno"
  repository       = "https://kyverno.github.io/kyverno"
  chart            = "kyverno"
  version          = var.kyverno_chart_version
  namespace        = "kyverno"
  create_namespace = true
  wait             = true
  timeout          = 600
}

# ClusterPolicy CRDs are not known to the Kubernetes provider at plan time,
# so the policies are applied with kubectl after the chart is ready.
resource "terraform_data" "kyverno_policies" {
  depends_on = [helm_release.kyverno]

  triggers_replace = {
    policies = sha256(join("", [
      for file in sort(fileset(var.policies_dir, "*.yaml")) :
      filesha256("${var.policies_dir}/${file}")
    ]))
  }

  provisioner "local-exec" {
    interpreter = ["bash", "-c"]
    command     = <<-EOT
      set -euo pipefail
      export KUBECONFIG='${var.kubeconfig_path}'
      kubectl wait --for=condition=Established crd/clusterpolicies.kyverno.io --timeout=180s
      kubectl apply -f '${var.policies_dir}'
    EOT
  }
}
