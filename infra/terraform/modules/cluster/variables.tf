variable "cluster_name" {
  type        = string
  description = "kind cluster name."
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
}
