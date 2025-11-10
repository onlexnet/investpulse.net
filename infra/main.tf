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
  wait_timer = contains(["prod", "production"], var.envName) ? 300 : 0 # 5 minutes for production

}

resource "github_actions_environment_secret" "static_web_app_api_token" {
  repository      = var.github_repository
  environment     = var.envName
  secret_name     = "AZURE_STATIC_WEB_APPS_API_TOKEN"
  plaintext_value = azurerm_static_web_app.webapp.api_key
}

# ================================================================
# Cloudflare DNS Configuration
# ================================================================

# Create DNS record for the environment
# Format: envName.investpulse.net -> Azure Static Web App
resource "cloudflare_record" "environment_dns" {
  zone_id = var.cloudflare_zone_id
  name    = var.envName # Environment name as DNS prefix (e.g., dev1)
  type    = "CNAME"
  content = azurerm_static_web_app.webapp.default_host_name
  ttl     = 60    # 1 minute TTL (can be custom when proxied = false)
  proxied = false # DNS only - direct connection to Azure Static Web App

  comment = "DNS record for ${var.envName} environment pointing to Azure Static Web App"
}

# ================================================================
# Azure Key Vault for Development Secrets
# ================================================================

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "dev_secrets" {
  name                = "${var.envName}-kw2-devs"
  location            = azurerm_resource_group.webapp.location
  resource_group_name = azurerm_resource_group.webapp.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
  

  # Enable for development access
  enabled_for_deployment          = false
  enabled_for_disk_encryption     = false
  enabled_for_template_deployment = true

  # Development-friendly settings
  purge_protection_enabled   = false
  soft_delete_retention_days = 7

  # Allow public access for development (restrict in production)
  public_network_access_enabled = true

  tags = merge(local.common_tags, {
    Purpose = "Development Secrets"
  })
}

# Access policy for developers (adjust based on your team's Azure AD group)
resource "azurerm_key_vault_access_policy" "developers" {
  key_vault_id = azurerm_key_vault.dev_secrets.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.developer_group_object_id 

  secret_permissions = [
    "Get",
    "List"
  ]
}

# Access policy for developers (adjust based on your team's Azure AD group)
resource "azurerm_key_vault_access_policy" "support" {
  key_vault_id = azurerm_key_vault.dev_secrets.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.support_group_object_id 
  

  secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete"
  ]
}

# Twitter API secrets
resource "azurerm_key_vault_secret" "twitter_api_key" {
  name         = "twitter-api-key"
  value        = var.twitter_api_key
  key_vault_id = azurerm_key_vault.dev_secrets.id

  depends_on = [
    azurerm_key_vault_access_policy.developers,
    azurerm_key_vault_access_policy.support]

  tags = {
    Environment = var.envName
    Purpose     = "Twitter API Integration"
  }

  lifecycle {
    ignore_changes = [
      # Ignore changes to the secret value as Terraform contains only placeholder value
      value
    ]
  }
}

resource "azurerm_key_vault_secret" "twitter_api_secret" {
  name         = "twitter-api-secret"
  value        = var.twitter_api_secret
  key_vault_id = azurerm_key_vault.dev_secrets.id

  depends_on = [
    azurerm_key_vault_access_policy.developers,
    azurerm_key_vault_access_policy.support]

  tags = {
    Environment = var.envName
    Purpose     = "Twitter API Integration"
  }

  lifecycle {
    ignore_changes = [
      # Ignore changes to the secret value as Terraform contains only placeholder value
      value
    ]
  }
}

resource "azurerm_key_vault_secret" "twitter_bearer_token" {
  name         = "twitter-bearer-token"
  value        = var.twitter_bearer_token
  key_vault_id = azurerm_key_vault.dev_secrets.id
  
  depends_on = [
    azurerm_key_vault_access_policy.developers,
    azurerm_key_vault_access_policy.support]
  
  tags = {
    Environment = var.envName
    Purpose     = "Twitter API Integration"
  }

  lifecycle {
    ignore_changes = [
      # Ignore changes to the secret value as Terraform contains only placeholder value
      value
    ]
  }
}
