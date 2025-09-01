# Local values for complex configurations
locals {
  # Environment-driven resource names using envName as prefix
  resource_group_name   = "${var.envName}-investpulse-rg"
  static_web_app_name   = "${var.envName}-investpulse-webapp"
  custom_domain         = "${var.envName}.${var.base_domain}"
  
  # Common tags for all resources
  common_tags = {
    Project     = "InvestPulse"
    Environment = var.envName
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
