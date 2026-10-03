variable "kyverno_chart_version" {
  type        = string
  description = "kyverno Helm chart version. App version tracks Kyverno itself."
}

variable "policies_dir" {
  type        = string
  description = "Absolute path to policies/kyverno."
}

variable "kubeconfig_path" {
  type        = string
  description = "Kubeconfig written by the cluster root."
}
