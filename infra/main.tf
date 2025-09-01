# Infrastructure Cost Summary (Monthly):
# ================================
# Azure Static Web App (Free): $0 USD/month
# Resource Group: Free
# Custom Domain: Included (up to 2 domains)
# ================================
# Total Estimated Cost: $0 USD/month
#
# Free tier limitations:
# - 0.5 GB bandwidth per month
# - Up to 2 custom domains
# - No APIs/functions support
# - Basic authentication only
#
# Cost optimization strategies:
# 1. Use Free tier for development/low-traffic sites
# 2. Monitor bandwidth usage to avoid overages
# 3. Consider CDN for static assets if bandwidth becomes an issue
# 4. Use GitHub Pages as alternative free hosting option

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.42"
    }
  }
  required_version = ">= 1.10"
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

resource "azurerm_resource_group" "webapp" {
  name     = var.resource_group_name
  location = var.location
  
  tags = local.common_tags
  
  # Cost: Resource groups are free - no charges for the container itself
}

resource "azurerm_static_web_app" "webapp" {
  name                = var.static_web_app_name
  resource_group_name = azurerm_resource_group.webapp.name
  location            = azurerm_resource_group.webapp.location
  sku_tier            = "Free"
  sku_size            = "Free"
  
  # Configuration for Next.js static export
  app_settings = local.app_settings
  
  tags = local.common_tags
}

# Custom domain binding (manual DNS validation required)
# Cost: Custom domains are included in Free plan (up to 2 domains)
resource "azurerm_static_web_app_custom_domain" "custom_domain" {
  static_web_app_id = azurerm_static_web_app.webapp.id
  domain_name       = var.custom_domain
  validation_type   = "cname-delegation"
}

# Outputs for DNS verification
output "static_web_app_default_hostname" {
  description = "Default hostname of the Static Web App - use this as CNAME target"
  value       = azurerm_static_web_app.webapp.default_host_name
}

output "custom_domain_validation_token" {
  description = "Domain validation token (if using TXT record validation)"
  value       = azurerm_static_web_app_custom_domain.custom_domain.validation_token
  sensitive   = true
}

# Note: GitHub Environments require GitHub Pro/Team/Enterprise plan
# For free GitHub accounts, environments are not available in private repos
# and have limited functionality in public repos
#
# Manual alternative: Create environments manually in GitHub UI
# Repository Settings > Environments > New environment

# Manual GitHub Environments Setup Instructions
output "github_environments_setup_instructions" {
  description = "Manual setup instructions for GitHub Environments"
  value = <<-EOT
    GitHub Environments require Pro/Team/Enterprise plan for full features.
    
    Manual setup:
    1. Go to: https://github.com/${var.github_owner}/${var.github_repository}/settings/environments
    2. Create environments: 'development', 'production'
    3. Configure protection rules in 'production':
       - Required reviewers
       - Wait timer: 5 minutes
       - Restrict to protected branches
    4. Add environment secrets as needed
    
    For Azure Static Web App deployment:
    - Environment name should match branch strategy
    - Add AZURE_STATIC_WEB_APPS_API_TOKEN secret to each environment
  EOT
}

output "azure_static_web_app_deployment_token_instruction" {
  description = "Instructions for obtaining deployment token"
  value = "Get deployment token from: Azure Portal > ${azurerm_static_web_app.webapp.name} > Manage deployment token"
}

