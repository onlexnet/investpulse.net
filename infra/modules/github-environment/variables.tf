variable "repository" {
  description = "GitHub repository name"
  type        = string
}

variable "environment_name" {
  description = "Name of the GitHub environment"
  type        = string
}

variable "can_admins_bypass" {
  description = "Whether repository admins can bypass environment protection rules"
  type        = bool
  default     = true
}

variable "prevent_self_review" {
  description = "Prevent users from approving their own workflow runs"
  type        = bool
  default     = false
}

variable "wait_timer" {
  description = "Wait time in seconds before allowing deployments to proceed"
  type        = number
  default     = 0
}

variable "secrets" {
  description = "Map of secret names to their values"
  type        = map(string)
  default     = {}
  # Note: Individual secret values are sensitive, but the map keys are not
}
