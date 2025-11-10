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

resource "azurerm_resource_group" "webapp" {
  name     = var.resource_group_name
  location = var.location

  tags = var.tags

  # Cost: Resource groups are free - no charges for the container itself
}

resource "azurerm_static_web_app" "webapp" {
  name                = var.static_web_app_name
  resource_group_name = azurerm_resource_group.webapp.name
  location            = azurerm_resource_group.webapp.location
  sku_tier            = "Free"
  sku_size            = "Free"

  # Configuration for Next.js static export
  app_settings = var.app_settings

  tags = var.tags
}

# Custom domain binding (manual DNS validation required)
# Cost: Custom domains are included in Free plan (up to 2 domains)
resource "azurerm_static_web_app_custom_domain" "custom_domain" {
  static_web_app_id = azurerm_static_web_app.webapp.id
  domain_name       = var.custom_domain
  validation_type   = "cname-delegation"
}
