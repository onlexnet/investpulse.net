output "record_id" {
  description = "ID of the DNS record"
  value       = cloudflare_record.dns_record.id
}

output "record_hostname" {
  description = "Hostname (FQDN) of the DNS record"
  value       = cloudflare_record.dns_record.hostname
}

output "record_name" {
  description = "Name of the DNS record"
  value       = cloudflare_record.dns_record.name
}

output "record_value" {
  description = "Value of the DNS record"
  value       = cloudflare_record.dns_record.content
}
