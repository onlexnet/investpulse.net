# Infrastructure Outputs
# ================================

# Environment Configuration
output "environment_info" {
  description = "Environment configuration details"
  value = {
    environment_name   = var.envName
    resource_group     = local.resource_group_name
    static_web_app     = local.static_web_app_name
    custom_domain      = local.custom_domain
    github_environment = var.envName
  }
}

# Azure Resources
output "azure_static_web_app_info" {
  description = "Azure Static Web App details"
  value = {
    name                = local.static_web_app_name
    resource_group_name = module.static_webapp.resource_group_name
    location            = module.static_webapp.resource_group_location
    default_hostname    = module.static_webapp.static_web_app_default_host_name
    custom_domain       = module.static_webapp.custom_domain_name
  }
}

output "resource_group_info" {
  description = "Resource group details"
  value = {
    name     = module.static_webapp.resource_group_name
    location = module.static_webapp.resource_group_location
  }
}

# DNS and Domain Information
output "dns_info" {
  description = "DNS configuration details"
  value = {
    custom_domain          = local.custom_domain
    azure_default_hostname = module.static_webapp.static_web_app_default_host_name
    environment_url        = "https://${module.cloudflare_dns.record_hostname}"
    dns_configured         = true
  }
}

# GitHub Environment Information
output "github_environment_info" {
  description = "GitHub environment details"
  value = {
    environment_name = module.github_environment.environment_name
    repository       = var.github_repository
    setup_url        = "https://github.com/${var.github_owner}/${var.github_repository}/settings/environments/${var.envName}"
  }
}

# Key Vault Information
output "key_vault_info" {
  description = "Key Vault details"
  value = {
    name = module.key_vault.key_vault_name
    uri  = module.key_vault.key_vault_uri
  }
}

# Deployment Instructions
output "deployment_instructions" {
  description = "Instructions for deploying to this environment"
  value       = <<-EOT
    Environment: ${var.envName}
    
    Resource Names Created:
    - Resource Group: ${local.resource_group_name}
    - Static Web App: ${local.static_web_app_name}
    - GitHub Environment: ${var.envName}
    - DNS: ${local.custom_domain}
    - Key Vault: ${module.key_vault.key_vault_name}
    
    Next Steps:
    1. Get Azure Static Web App deployment token:
       Azure Portal > ${local.static_web_app_name} > Manage deployment token
    
    2. Configure GitHub Environment Secret:
       Go to: https://github.com/${var.github_owner}/${var.github_repository}/settings/environments/${var.envName}
       Add secret: AZURE_STATIC_WEB_APPS_API_TOKEN
    
    3. Access your deployed app:
       URL: https://${module.cloudflare_dns.record_hostname}
  EOT
}