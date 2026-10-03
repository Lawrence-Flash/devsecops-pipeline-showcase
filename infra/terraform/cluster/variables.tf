variable "cluster_name" {
  type    = string
  default = "devsecops-lab"
}

variable "host_port" {
  type    = number
  default = 30080
}

variable "app_image" {
  type        = string
  default     = "tickets-api:local"
  description = "Image name:tag already present in the local Docker daemon."
}
