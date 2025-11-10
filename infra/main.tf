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

# ================================================================
# Azure Static Web App Module
# ================================================================

module "static_webapp" {
  source = "./modules/azure-static-webapp"

  resource_group_name = local.resource_group_name
  location            = var.location
  static_web_app_name = local.static_web_app_name
  custom_domain       = local.custom_domain
  app_settings        = local.app_settings
  tags                = local.common_tags
}

# ================================================================
# GitHub Environment Module
# ================================================================

module "github_environment" {
  source = "./modules/github-environment"

  repository          = var.github_repository
  environment_name    = var.envName
  can_admins_bypass   = true
  prevent_self_review = false
  wait_timer          = contains(["prod", "production"], var.envName) ? 300 : 0

  secrets = {
    AZURE_STATIC_WEB_APPS_API_TOKEN = module.static_webapp.static_web_app_api_key
  }
}

# ================================================================
# Cloudflare DNS Module
# ================================================================

module "cloudflare_dns" {
  source = "./modules/cloudflare-dns"

  zone_id      = var.cloudflare_zone_id
  record_name  = var.envName
  record_type  = "CNAME"
  record_value = module.static_webapp.static_web_app_default_host_name
  ttl          = 60
  proxied      = false
  comment      = "DNS record for ${var.envName} environment pointing to Azure Static Web App"
}

# ================================================================
# Azure Key Vault Module
# ================================================================

data "azurerm_client_config" "current" {}

module "key_vault" {
  source = "./modules/key-vault"

  key_vault_name      = "${var.envName}-kw2-devs"
  location            = module.static_webapp.resource_group_location
  resource_group_name = module.static_webapp.resource_group_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  enabled_for_deployment          = false
  enabled_for_disk_encryption     = false
  enabled_for_template_deployment = true
  purge_protection_enabled        = false
  soft_delete_retention_days      = 7
  public_network_access_enabled   = true

  access_policies = [
    {
      object_id          = var.developer_group_object_id
      secret_permissions = ["Get", "List"]
    },
    {
      object_id          = var.support_group_object_id
      secret_permissions = ["Get", "List", "Set", "Delete"]
    }
  ]

  secrets = {
    "twitter-api-key" = {
      value = var.twitter_api_key
      tags = {
        Environment = var.envName
        Purpose     = "Twitter API Integration"
      }
    }
    "twitter-api-secret" = {
      value = var.twitter_api_secret
      tags = {
        Environment = var.envName
        Purpose     = "Twitter API Integration"
      }
    }
    "twitter-bearer-token" = {
      value = var.twitter_bearer_token
      tags = {
        Environment = var.envName
        Purpose     = "Twitter API Integration"
      }
    }
  }

  tags = merge(local.common_tags, {
    Purpose = "Development Secrets"
  })
}
