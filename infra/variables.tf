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

variable "github_repository" {
  description = "Name of the GitHub repository"
  type        = string
  default     = "investpulse.net"
}

variable "github_owner" {
  description = "Owner of the GitHub repository"
  type        = string
  default     = "onlexnet"
}
# Note: GitHub configuration removed - environments require Pro/Enterprise plan
# Manual setup required for GitHub Actions deployment

# Note: GitHub Environments configuration removed due to plan limitations
# Manual setup required in GitHub UI for free/basic plans