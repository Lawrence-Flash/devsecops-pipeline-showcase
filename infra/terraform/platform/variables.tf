variable "namespace" {
  type    = string
  default = "tickets"
}

variable "image_repository" {
  type    = string
  default = "tickets-api"
}

variable "image_tag" {
  type    = string
  default = "local"
}

variable "node_port" {
  type    = number
  default = 30080
}

variable "lab_api_key" {
  type        = string
  default     = "lab-demo-key"
  description = "Lab placeholder. Override it if you want; do not put a real secret in git."
}

variable "kyverno_chart_version" {
  type    = string
  default = "3.9.1"
}
