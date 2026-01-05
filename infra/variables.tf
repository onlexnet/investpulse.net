# Environment Configuration
variable "envName" {
  description = "Environment name used as prefix for DNS, GitHub environment, and resource group"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.envName))
    error_message = "Environment name must contain only lowercase letters, numbers, and hyphens."
  }
}

# Azure Configuration
variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  default     = "ac0e7cdd-3111-4671-a602-0d93afb5df20"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "westeurope"
}

variable "base_domain" {
  description = "Base domain for DNS entries"
  type        = string
  default     = "investpulse.net"
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

variable "GITHUB_TOKEN" {
  description = "GitHub Personal Access Token with repo and admin:org permissions"
  type        = string
  sensitive   = true
}

# Cloudflare Configuration
variable "CLOUDFLARE_API_TOKEN" {
  description = "Cloudflare API token for DNS management"
  type        = string
  sensitive   = true
}

variable "cloudflare_zone_id" {
  description = "Cloudflare Zone ID for investpulse.net domain"
  type        = string
  default     = "2fa34bc4e1284682e9047b76b5826ffd"
}

# Finnhub.io API Configuration
variable "FINNHUB_API_KEY" {
  description = "Finnhub.io API key for stock market data"
  type        = string
  sensitive   = true
  
  validation {
    condition     = var.FINNHUB_API_KEY != ""
    error_message = "FINNHUB_API_KEY must be set. Obtain a free API key from https://finnhub.io/register"
  }
}