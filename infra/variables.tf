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

variable "developer_group_object_id" {
  description = "Azure AD Object ID for the developer group to assign permissions"
  type        = string
  default     = "b4f82f7d-49cb-4ada-8001-6da6f159409b"
}

variable "support_group_object_id" {
  description = "Azure AD Object ID for the support group to assign permissions"
  type        = string
  default     = "50a70998-40ec-4d62-aa19-e24513b2ec6d"
}

variable "twitter_api_secret" {
  description = "Twitter API secret for application integration"
  type        = string
  sensitive   = true
  default     = "twitter_api_secret placeholder"
}
variable "twitter_api_key" {
  description = "Twitter API key for application integration"
  type        = string
  sensitive   = true
  default     = "twitter_api_key placeholder"
}
variable "twitter_bearer_token" {
  description = "Twitter Bearer Token for API authentication"
  type        = string
  sensitive   = true
  default     = "twitter_bearer_token placeholder"
}
