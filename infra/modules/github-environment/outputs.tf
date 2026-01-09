output "environment_name" {
  description = "Name of the created GitHub environment"
  value       = github_repository_environment.environment.environment
}

output "environment_id" {
  description = "ID of the GitHub environment"
  value       = github_repository_environment.environment.id
}
