variable "key_vault_name" {
  description = "Name of the Azure Key Vault"
  type        = string
}

variable "location" {
  description = "Azure region for the Key Vault"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "tenant_id" {
  description = "Azure AD tenant ID"
  type        = string
}

variable "sku_name" {
  description = "SKU name for the Key Vault"
  type        = string
  default     = "standard"
}

variable "enabled_for_deployment" {
  description = "Enable Azure Virtual Machines to retrieve certificates"
  type        = bool
  default     = false
}

variable "enabled_for_disk_encryption" {
  description = "Enable Azure Disk Encryption to retrieve secrets"
  type        = bool
  default     = false
}

variable "enabled_for_template_deployment" {
  description = "Enable Azure Resource Manager to retrieve secrets"
  type        = bool
  default     = true
}

variable "purge_protection_enabled" {
  description = "Enable purge protection"
  type        = bool
  default     = false
}

variable "soft_delete_retention_days" {
  description = "Number of days to retain deleted vaults"
  type        = number
  default     = 7
}

variable "public_network_access_enabled" {
  description = "Enable public network access"
  type        = bool
  default     = true
}

variable "access_policies" {
  description = "List of access policies for the Key Vault"
  type = list(object({
    object_id          = string
    secret_permissions = list(string)
  }))
  default = []
}

variable "secrets" {
  description = "Map of secrets to create in the Key Vault"
  type = map(object({
    value = string
    tags  = map(string)
  }))
  default = {}
  # Note: Individual secret values are sensitive, but the map keys are not
}

variable "tags" {
  description = "Tags to apply to the Key Vault"
  type        = map(string)
  default     = {}
}
