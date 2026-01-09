# ================================================================
# Azure Key Vault for Development Secrets
# ================================================================

resource "azurerm_key_vault" "vault" {
  name                = var.key_vault_name
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id
  sku_name            = var.sku_name

  # Enable for development access
  enabled_for_deployment          = var.enabled_for_deployment
  enabled_for_disk_encryption     = var.enabled_for_disk_encryption
  enabled_for_template_deployment = var.enabled_for_template_deployment

  # Development-friendly settings
  purge_protection_enabled   = var.purge_protection_enabled
  soft_delete_retention_days = var.soft_delete_retention_days

  # Allow public access for development (restrict in production)
  public_network_access_enabled = var.public_network_access_enabled

  tags = var.tags
}

# Access policies for Key Vault
resource "azurerm_key_vault_access_policy" "policies" {
  for_each = { for idx, policy in var.access_policies : idx => policy }

  key_vault_id = azurerm_key_vault.vault.id
  tenant_id    = var.tenant_id
  object_id    = each.value.object_id

  secret_permissions = each.value.secret_permissions
}

# Secrets
resource "azurerm_key_vault_secret" "secrets" {
  for_each = var.secrets

  name         = each.key
  value        = each.value.value
  key_vault_id = azurerm_key_vault.vault.id

  tags = each.value.tags

  depends_on = [azurerm_key_vault_access_policy.policies]

  lifecycle {
    ignore_changes = [
      # Ignore changes to the secret value as Terraform contains only placeholder value
      value
    ]
  }
}
