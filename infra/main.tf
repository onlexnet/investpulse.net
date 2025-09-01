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
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.10"
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# GitHub provider with enhanced permissions
provider "github" {
  owner = var.github_owner
  token = var.github_token
}

# Cloudflare provider for DNS management
provider "cloudflare" {
  api_token = var.cloudflare_api_token
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

# GitHub Environments with workaround for free plan limitations
# ================================================================

# Try to create environments - will work on public repos or paid plans
# COMMENTED OUT: Requires GitHub token with admin:org permissions
resource "github_repository_environment" "environments" {

  for_each = toset([
    "development",
    "production"
  ])

  repository  = var.github_repository
  environment = each.key


  # Basic configuration that works on free plans
  can_admins_bypass   = true
  prevent_self_review = false

  # Wait timer only for production
  # wait_timer = each.key == "production" ? 300 : 0  # 5 minutes for prod

  # Deployment branch policy (works on public repos)
  # dynamic "deployment_branch_policy" {
  #   for_each = each.key == "production" ? [1] : []
  #   content {
  #     protected_branches     = true
  #     custom_branch_policies = false
  #   }
  # }

  # Note: reviewers require GitHub Pro/Team/Enterprise
  # For free accounts, this will be ignored
  # lifecycle {
  #   ignore_changes = [
  #     reviewers  # Ignore reviewer changes as they require paid plan
  #   ]
  # }
}

# Environment variables/secrets setup instructions
locals {
  environment_setup_instructions = {
    development = {
      name = "development"
      secrets_needed = [
        "AZURE_STATIC_WEB_APPS_API_TOKEN"
      ]
      description = "Development environment for feature branches"
    }
    production = {
      name = "production"
      secrets_needed = [
        "AZURE_STATIC_WEB_APPS_API_TOKEN"
      ]
      description = "Production environment for main branch"
    }
  }
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
  value       = <<-EOT
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

# ================================================================
# Cloudflare DNS Configuration
# ================================================================

# Create DNS records for each GitHub environment
# Format: environment.investpulse.net -> Azure Static Web App
resource "cloudflare_record" "environment_dns" {
  for_each = var.cloudflare_zone_id != "" ? toset([
    "development",
    "production"
  ]) : toset([])

  zone_id = var.cloudflare_zone_id
  name    = each.key  # Environment name (development, production)
  type    = "CNAME"
  content = azurerm_static_web_app.webapp.default_host_name
  ttl     = 300   # 5 minutes TTL (can be custom when proxied = false)
  proxied = false # DNS only - direct connection to Azure Static Web App

  comment = "DNS record for ${each.key} environment pointing to Azure Static Web App"

  # Note: tags removed due to Cloudflare plan limitations
}

output "azure_static_web_app_deployment_token_instruction" {
  description = "Instructions for obtaining deployment token"
  value       = "Get deployment token from: Azure Portal > ${azurerm_static_web_app.webapp.name} > Manage deployment token"
}

# GitHub Environments Information
# COMMENTED OUT: Requires GitHub environments to be created first
# output "github_environments_created" {
#   description = "Information about created GitHub environments"
#   value = {
#     for env_name, env in github_repository_environment.environments : env_name => {
#       id          = env.id
#       environment = env.environment
#       repository  = env.repository
#       wait_timer  = env.wait_timer
#     }
#   }
# }

output "environment_setup_guide" {
  description = "Guide for setting up environment secrets"
  value = {
    for env_name, config in local.environment_setup_instructions : env_name => {
      name           = config.name
      description    = config.description
      secrets_needed = config.secrets_needed
      setup_url      = "https://github.com/${var.github_owner}/${var.github_repository}/settings/environments/${config.name}"
    }
  }
}

# Cloudflare DNS Records Information
output "cloudflare_dns_records" {
  description = "Information about created Cloudflare DNS records"
  value = {
    for env_name, record in cloudflare_record.environment_dns : env_name => {
      hostname = record.hostname
      name     = record.name
      type     = record.type
      content  = record.content
      proxied  = record.proxied
      url      = "https://${record.hostname}"
    }
  }
}

output "environment_urls" {
  description = "URLs for each environment"
  value = {
    for env_name, record in cloudflare_record.environment_dns : env_name => "https://${record.hostname}"
  }
}

output "cloudflare_setup_instructions" {
  description = "Instructions for setting up Cloudflare DNS"
  value = "Cloudflare DNS is configured and ready to deploy - single CNAME record for investpulse.net"
}

