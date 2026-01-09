variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "static_web_app_name" {
  description = "Name of the Azure Static Web App"
  type        = string
}

variable "custom_domain" {
  description = "Custom domain name for the static web app"
  type        = string
}

variable "app_settings" {
  description = "Application settings for the static web app"
  type        = map(string)
  default     = {}
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
