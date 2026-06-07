terraform {
  required_providers {
    kubernetes = {
      source  = "opentofu/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "kind-ship-it"
}

resource "kubernetes_namespace" "ship_it" {
  metadata {
    name = var.namespace
    labels = {
      managed-by = "opentofu"
      project    = "ship-it"
    }
  }
}

resource "kubernetes_resource_quota" "ship_it" {
  metadata {
    name      = "ship-it-quota"
    namespace = kubernetes_namespace.ship_it.metadata[0].name
  }
  spec {
    hard = {
      "requests.cpu"    = "500m"
      "requests.memory" = "256Mi"
      "limits.cpu"      = "1000m"
      "limits.memory"   = "512Mi"
      pods              = "10"
    }
  }
}

resource "kubernetes_limit_range" "ship_it" {
  metadata {
    name      = "ship-it-limits"
    namespace = kubernetes_namespace.ship_it.metadata[0].name
  }
  spec {
    limit {
      type = "Container"
      default = {
        cpu    = "200m"
        memory = "128Mi"
      }
      default_request = {
        cpu    = "100m"
        memory = "64Mi"
      }
    }
  }
}
