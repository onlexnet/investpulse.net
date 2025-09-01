# Azure Configuration
variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  default     = "ac0e7cdd-3111-4671-a602-0d93afb5df20"
}

variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
  default     = "investpulse-webapp-rg"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "westeurope"
}

variable "static_web_app_name" {
  description = "Name of the Azure Static Web App"
  type        = string
  default     = "investpulse-webapp"
}

variable "custom_domain" {
  description = "Custom domain for the web app"
  type        = string
  default     = "dev.investpulse.net"
}

# GitHub Configuration
variable "github_owner" {
  description = "GitHub repository owner/organization"
  type        = string
  default     = "onlexnet"
}

variable "github_repository" {
  description = "GitHub repository name"
  type        = string
}

variable "github_token" {
  description = "GitHub Personal Access Token with repo and admin:org permissions"
  type        = string
  sensitive   = true
}

# Cloudflare Configuration
variable "cloudflare_api_token" {
  description = "Cloudflare API token for DNS management"
  type        = string
  sensitive   = true
}

variable "cloudflare_zone_id" {
  description = "Cloudflare Zone ID for investpulse.net domain"
  type        = string
  default     = "2fa34bc4e1284682e9047b76b5826ffd"
}