variable "cluster_name" {
  type        = string
  description = "kind cluster name."

  validation {
    condition     = can(regex("^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", var.cluster_name))
    error_message = "Use a kind cluster name of lowercase letters, digits, and hyphens, with no spaces or quotes."
  }
}

variable "kubeconfig_path" {
  type        = string
  description = "Where kind writes the kubeconfig. The platform root reads this path."
}

variable "host_port" {
  type        = number
  description = "Host port mapped to the kind node. The app Service uses this as a NodePort."
}

variable "app_image" {
  type        = string
  description = "Local image to load into the kind nodes. Build it before apply."

  validation {
    condition     = can(regex("^[A-Za-z0-9][A-Za-z0-9._:/@-]{0,127}$", var.app_image))
    error_message = "Use an image reference without spaces or quotes, for example tickets-api:local. The value is passed to kind with no shell quoting."
  }
}
