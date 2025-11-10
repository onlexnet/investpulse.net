# GitHub Environment based on environment_name
resource "github_repository_environment" "environment" {
  repository  = var.repository
  environment = var.environment_name

  # Basic configuration that works on free plans
  can_admins_bypass   = var.can_admins_bypass
  prevent_self_review = var.prevent_self_review

  # Wait timer for production-like environments
  wait_timer = var.wait_timer
}

# Create environment secrets
resource "github_actions_environment_secret" "secrets" {
  for_each = var.secrets

  repository      = var.repository
  environment     = var.environment_name
  secret_name     = each.key
  plaintext_value = each.value

  depends_on = [github_repository_environment.environment]
}
