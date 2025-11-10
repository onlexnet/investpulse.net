# ================================================================
# Cloudflare DNS Configuration
# ================================================================

# Create DNS record for the environment
resource "cloudflare_record" "dns_record" {
  zone_id = var.zone_id
  name    = var.record_name
  type    = var.record_type
  content = var.record_value
  ttl     = var.ttl
  proxied = var.proxied

  comment = var.comment != "" ? var.comment : "Managed by Terraform"
}
