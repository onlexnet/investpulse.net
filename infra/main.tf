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
  cloud {
    organization = "onlexnet"

    workspaces {
      project = "investpulse"
      name    = "investpulse-nonprod"
    }
  }

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
  token = var.GITHUB_TOKEN
}

# Cloudflare provider for DNS management
provider "cloudflare" {
  api_token = var.CLOUDFLARE_API_TOKEN
}

resource "azurerm_resource_group" "webapp" {
  name     = local.resource_group_name
  location = var.location

  tags = local.common_tags

  # Cost: Resource groups are free - no charges for the container itself
}

resource "azurerm_static_web_app" "webapp" {
  name                = local.static_web_app_name
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
  domain_name       = local.custom_domain
  validation_type   = "cname-delegation"
}

# GitHub Environment based on envName
resource "github_repository_environment" "environment" {
  repository  = var.github_repository
  environment = var.envName

  # Basic configuration that works on free plans
  can_admins_bypass   = true
  prevent_self_review = false

  # Wait timer for production-like environments
  wait_timer = contains(["prod", "production"], var.envName) ? 300 : 0  # 5 minutes for production

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
}

# ================================================================
# Cloudflare DNS Configuration
# ================================================================

# Create DNS record for the environment
# Format: envName.investpulse.net -> Azure Static Web App
resource "cloudflare_record" "environment_dns" {
  count = var.cloudflare_zone_id != "" ? 1 : 0

  zone_id = var.cloudflare_zone_id
  name    = var.envName  # Environment name as DNS prefix (e.g., dev1)
  type    = "CNAME"
  content = azurerm_static_web_app.webapp.default_host_name
  ttl     = 60   # 1 minute TTL (can be custom when proxied = false)
  proxied = false # DNS only - direct connection to Azure Static Web App

  comment = "DNS record for ${var.envName} environment pointing to Azure Static Web App"
}
