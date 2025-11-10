#!/bin/bash

# Load development secrets from Azure Key Vault
# Usage: source ./scripts/load-dev-secrets.sh [environment]

set -e

ENVIRONMENT=${1:-dev1}
KEY_VAULT_NAME="dev-kw2-devs"

# Check if Azure CLI is logged in
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure CLI. Please run: az login"
    return 1
fi

# Check if Key Vault exists and is accessible
if ! az keyvault show --name "$KEY_VAULT_NAME" &> /dev/null; then
    echo "❌ Cannot access Key Vault: $KEY_VAULT_NAME"
    echo "Please ensure you have access and the Key Vault exists."
    return 1
fi

echo "🔐 Loading secrets from Key Vault: $KEY_VAULT_NAME"

# Load Twitter API secrets
export TWITTER_API_KEY=$(az keyvault secret show --vault-name "$KEY_VAULT_NAME" --name "twitter-api-key" --query value -o tsv)
export TWITTER_API_SECRET=$(az keyvault secret show --vault-name "$KEY_VAULT_NAME" --name "twitter-api-secret" --query value -o tsv)

# Verify secrets are loaded
if [[ -n "$TWITTER_API_KEY" && -n "$TWITTER_API_SECRET" ]]; then
    echo "✅ Successfully loaded secrets:"
    echo "   - TWITTER_API_KEY: ${TWITTER_API_KEY:0:8}..."
    echo "   - TWITTER_API_SECRET: ${TWITTER_API_SECRET:0:8}..."
else
    echo "❌ Failed to load one or more secrets"
    return 1
fi

echo "🚀 Environment variables are now available in your session"
