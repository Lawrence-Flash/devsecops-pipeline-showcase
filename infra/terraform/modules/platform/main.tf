resource "helm_release" "kyverno" {
  name             = "kyverno"
  repository       = "https://kyverno.github.io/kyverno"
  chart            = "kyverno"
  version          = var.kyverno_chart_version
  namespace        = "kyverno"
  create_namespace = true
  wait             = true
  timeout          = 900
  # A failed install is uninstalled. A failed upgrade rolls back and
  # cleanup_on_fail removes resources that upgrade created. The next
  # `make up` can install or upgrade again instead of sticking on
  # "created but has a failed status".
  atomic          = true
  cleanup_on_fail = true

  values = [
    yamlencode({
      admissionController = {
        replicas = 1
      }
      # This lab only needs admission-time enforcement. The other
      # controllers use the same image and then schedule more pods.
      # On a 2 GB Docker Desktop VM those pods sit pending while the
      # image is still downloading, and Helm hits its deadline.
      backgroundController = {
        enabled = false
      }
      cleanupController = {
        enabled = false
      }
      reportsController = {
        enabled = false
      }
      features = {
        admissionReports = {
          enabled = false
        }
        aggregateReports = {
          enabled = false
        }
        policyReports = {
          enabled = false
        }
        validatingAdmissionPolicyReports = {
          enabled = false
        }
        backgroundScan = {
          enabled = false
        }
      }
      # Post-upgrade migration is for existing policies. A new kind cluster has none.
      crds = {
        migration = {
          enabled = false
        }
      }
    })
  ]
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

  # Default interpreter: /bin/sh on Linux and macOS, cmd.exe on Windows.
  # && and double quotes work in both. KUBECONFIG is set by Terraform,
  # not by export, and backslashes are normalized so cmd does not treat
  # them as escapes. A bash interpreter is not required.
  provisioner "local-exec" {
    command = "kubectl wait --for=condition=Established crd/clusterpolicies.kyverno.io --timeout=300s && kubectl apply -f \"${replace(var.policies_dir, "\\", "/")}\""
    environment = {
      KUBECONFIG = replace(var.kubeconfig_path, "\\", "/")
    }
  }
}
