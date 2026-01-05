# Infrastructure Outputs
# ================================

# Environment Configuration
output "environment_info" {
  description = "Environment configuration details"
  value = {
    environment_name    = var.envName
    resource_group      = local.resource_group_name
    static_web_app      = local.static_web_app_name
    custom_domain       = local.custom_domain
    github_environment  = var.envName
  }
}

# Azure Resources
output "azure_static_web_app_info" {
  description = "Azure Static Web App details"
  value = {
    name                = azurerm_static_web_app.webapp.name
    resource_group_name = azurerm_static_web_app.webapp.resource_group_name
    location           = azurerm_static_web_app.webapp.location
    default_hostname   = azurerm_static_web_app.webapp.default_host_name
    sku_tier           = azurerm_static_web_app.webapp.sku_tier
  }
}

output "resource_group_info" {
  description = "Resource group details"
  value = {
    name     = azurerm_resource_group.webapp.name
    location = azurerm_resource_group.webapp.location
    id       = azurerm_resource_group.webapp.id
  }
}

# DNS and Domain Information
output "dns_info" {
  description = "DNS configuration details"
  value = {
    custom_domain         = local.custom_domain
    azure_default_hostname = azurerm_static_web_app.webapp.default_host_name
    environment_url       = "https://${cloudflare_record.environment_dns.hostname}"
    dns_configured        = length(cloudflare_record.environment_dns) > 0
  }
}

# GitHub Environment Information
output "github_environment_info" {
  description = "GitHub environment details"
  value = {
    environment_name = github_repository_environment.environment.environment
    repository      = github_repository_environment.environment.repository
    wait_timer      = github_repository_environment.environment.wait_timer
    setup_url       = "https://github.com/${var.github_owner}/${var.github_repository}/settings/environments/${var.envName}"
  }
}

# Deployment Instructions
output "deployment_instructions" {
  description = "Instructions for deploying to this environment"
  value = <<-EOT
    Environment: ${var.envName}
    
    Resource Names Created:
    - Resource Group: ${local.resource_group_name}
    - Static Web App: ${local.static_web_app_name}
    - GitHub Environment: ${var.envName}
    - DNS: ${local.custom_domain}
    
    Next Steps:
    1. Get Azure Static Web App deployment token:
       Azure Portal > ${local.static_web_app_name} > Manage deployment token
    
    2. Configure GitHub Environment Secret:
       Go to: https://github.com/${var.github_owner}/${var.github_repository}/settings/environments/${var.envName}
       Add secret: AZURE_STATIC_WEB_APPS_API_TOKEN
    
    3. Configure Finnhub API Key:
       Set FINNHUB_API_KEY in Terraform variables or as a secret
    
    4. Access your deployed app:
       URL: https://${cloudflare_record.environment_dns.hostname}
       
    5. Test Finnhub API endpoints:
       - Quote: https://${cloudflare_record.environment_dns.hostname}/api/finnhub/quote?symbol=AAPL
       - Profile: https://${cloudflare_record.environment_dns.hostname}/api/finnhub/profile?symbol=AAPL
  EOT
}

# API Configuration
output "api_info" {
  description = "API upstream configuration"
  value = {
    api_location          = local.app_settings["api_location"]
    finnhub_configured    = var.FINNHUB_API_KEY != ""
    available_endpoints   = [
      "/api/finnhub/quote?symbol=<SYMBOL>",
      "/api/finnhub/profile?symbol=<SYMBOL>"
    ]
  }
  sensitive = false
}