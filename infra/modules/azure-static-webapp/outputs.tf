output "resource_group_name" {
  description = "Name of the created resource group"
  value       = azurerm_resource_group.webapp.name
}

output "resource_group_location" {
  description = "Location of the created resource group"
  value       = azurerm_resource_group.webapp.location
}

output "static_web_app_id" {
  description = "ID of the Azure Static Web App"
  value       = azurerm_static_web_app.webapp.id
}

output "static_web_app_api_key" {
  description = "API key for the Azure Static Web App"
  value       = azurerm_static_web_app.webapp.api_key
  sensitive   = true
}

output "static_web_app_default_host_name" {
  description = "Default hostname of the Azure Static Web App"
  value       = azurerm_static_web_app.webapp.default_host_name
}

output "custom_domain_name" {
  description = "Custom domain name configured for the static web app"
  value       = azurerm_static_web_app_custom_domain.custom_domain.domain_name
}
