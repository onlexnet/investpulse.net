# Local values for complex configurations
locals {
  # Common tags for all resources
  common_tags = {
    Project     = "InvestPulse"
    Environment = "production"
    ManagedBy   = "Terraform"
    Repository  = "${var.github_owner}/${var.github_repository}"
  }

  # Azure Static Web App configuration
  app_settings = {
    "app_location"                  = "/webapp"
    "output_location"               = "out"
    "app_build_command"             = "npm run build:static"
    "api_location"                  = ""
    "skip_github_api_orchestration" = "false"
  }
}
