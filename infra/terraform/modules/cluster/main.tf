resource "kind_cluster" "this" {
  name            = var.cluster_name
  wait_for_ready  = true
  kubeconfig_path = var.kubeconfig_path

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    node {
      role = "control-plane"

      extra_port_mappings {
        container_port = var.host_port
        host_port      = var.host_port
      }
    }
  }
}

# tehcyx/kind 0.11.0 does not ship the kind_load resource yet (it is on the
# provider's main branch, unpublished). This is `kind load docker-image`.
resource "terraform_data" "load_image" {
  depends_on = [kind_cluster.this]

  triggers_replace = {
    image   = var.app_image
    cluster = kind_cluster.this.name
  }

  # No interpreter and no quotes. On Windows, local-exec is cmd.exe, which
  # keeps single quotes as part of the argument, so kind looks up
  # "'tickets-api:local'" and reports that the image is missing.
  # cmd.exe and /bin/sh both accept this form. Names are validated
  # to contain no spaces or quotes.
  provisioner "local-exec" {
    command = "kind load docker-image ${var.app_image} --name ${kind_cluster.this.name}"
  }
}
