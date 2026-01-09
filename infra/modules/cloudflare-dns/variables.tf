variable "zone_id" {
  description = "Cloudflare Zone ID"
  type        = string
}

variable "record_name" {
  description = "DNS record name (subdomain or @ for root)"
  type        = string
}

variable "record_type" {
  description = "DNS record type (A, AAAA, CNAME, etc.)"
  type        = string
  default     = "CNAME"
}

variable "record_value" {
  description = "DNS record value (IP address or hostname)"
  type        = string
}

variable "ttl" {
  description = "Time to live for DNS record in seconds"
  type        = number
  default     = 60
}

variable "proxied" {
  description = "Whether the record should be proxied through Cloudflare"
  type        = bool
  default     = false
}

variable "comment" {
  description = "Comment to add to the DNS record"
  type        = string
  default     = ""
}
