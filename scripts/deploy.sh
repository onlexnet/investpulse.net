#!/bin/bash

# Deploy InvestPulse Infrastructure using Terraform
# Usage: ./scripts/deploy.sh [environment]
# Example: ./scripts/deploy.sh dev

set -euo pipefail

# Configuration
ENVIRONMENT=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INFRA_DIR="$REPO_ROOT/infra"

echo "🚀 Deploying InvestPulse infrastructure for environment: $ENVIRONMENT"
echo "📁 Infrastructure directory: $INFRA_DIR"

# Validate environment name
if [[ ! "$ENVIRONMENT" =~ ^[a-z0-9-]+$ ]]; then
  echo "❌ Error: Environment name must contain only lowercase letters, numbers, and hyphens"
  exit 1
fi

# Change to infrastructure directory
cd "$INFRA_DIR"

# Check if required files exist
if [ ! -f "main.tf" ]; then
  echo "❌ Error: main.tf not found in $INFRA_DIR"
  exit 1
fi

# Ensure Terraform is initialized
echo "🔧 Initializing Terraform..."
terraform init

# Validate Terraform configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Create terraform.tfvars if it doesn't exist
if [ ! -f "terraform.tfvars" ]; then
  echo "📝 Creating terraform.tfvars for environment: $ENVIRONMENT"
  cat > terraform.tfvars << EOF
# Environment Configuration
envName = "$ENVIRONMENT"

# GitHub Configuration  
github_repository = "investpulse.net"

# Note: Sensitive variables should be set via environment variables:
# export TF_VAR_github_token="your_github_token"
# export TF_VAR_cloudflare_api_token="your_cloudflare_token"
EOF
else
  echo "📄 Using existing terraform.tfvars"
fi

# Plan the deployment
echo "📋 Planning Terraform deployment..."
terraform plan -var="envName=$ENVIRONMENT"

# Apply the configuration
echo "🏗️  Applying Terraform configuration..."
terraform apply -var="envName=$ENVIRONMENT" -auto-approve

# Show outputs
echo "📊 Deployment outputs:"
terraform output

echo "✅ Deployment completed successfully!"
echo "🌐 Environment: $ENVIRONMENT"
echo "🔗 Expected domain: ${ENVIRONMENT}.investpulse.net"
echo ""
echo "📋 Next steps:"
echo "1. Get the Azure Static Web App deployment token from Azure Portal"
echo "2. Add it as AZURE_STATIC_WEB_APPS_API_TOKEN secret to GitHub environment: $ENVIRONMENT"
echo "3. Trigger a deployment via GitHub Actions"