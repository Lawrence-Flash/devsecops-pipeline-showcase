variable "namespace" {
  type = string
}

variable "chart_path" {
  type        = string
  description = "Absolute path to charts/tickets-api."
}

variable "image_repository" {
  type = string
}

variable "image_tag" {
  type = string
}

variable "node_port" {
  type = number
}

variable "lab_api_key" {
  type        = string
  description = "Lab-only API key injected into the pod. Not a real credential."
}
