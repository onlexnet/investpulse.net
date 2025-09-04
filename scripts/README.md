# Deployment Scripts

This directory contains automation scripts for building and deploying the InvestPulse application.

## Scripts

### `build_and_push.sh`

Builds static assets for the webapp.

**Usage:**
```bash
./scripts/build_and_push.sh [environment]
```

**Example:**
```bash
./scripts/build_and_push.sh dev
```

**What it does:**
1. Validates environment name format
2. Installs npm dependencies in the webapp directory
3. Cleans previous build output
4. Runs ESLint checks
5. Builds Next.js static export
6. Provides build statistics

**Requirements:**
- Node.js 18+
- npm
- Working directory must be repository root

### `deploy.sh`

Deploys infrastructure using Terraform.

**Usage:**
```bash
./scripts/deploy.sh [environment]
```

**Example:**
```bash
./scripts/deploy.sh dev
```

**What it does:**
1. Validates environment name format
2. Changes to infra directory
3. Initializes and validates Terraform
4. Creates terraform.tfvars if missing
5. Plans and applies Terraform configuration
6. Shows deployment outputs

**Requirements:**
- Terraform 1.10+
- Azure CLI authentication or service principal
- Required environment variables (see below)

## Environment Variables

### For Terraform Deployment

Set these environment variables before running `deploy.sh`:

```bash
# GitHub token for environment management
export TF_VAR_github_token="ghp_your_github_token"

# Cloudflare API token for DNS (optional)
export TF_VAR_cloudflare_api_token="your_cloudflare_token"

# Azure authentication (if using service principal)
export ARM_CLIENT_ID="your_client_id"
export ARM_CLIENT_SECRET="your_client_secret"
export ARM_SUBSCRIPTION_ID="your_subscription_id"
export ARM_TENANT_ID="your_tenant_id"
```

### For GitHub Actions

These are configured as secrets in GitHub Environments:
- `AZURE_STATIC_WEB_APPS_API_TOKEN`
- `CLOUDFLARE_API_TOKEN`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_TENANT_ID`

## Supported Environments

The scripts support any environment name that follows these rules:
- Contains only lowercase letters, numbers, and hyphens
- Used as DNS subdomain: `{environment}.investpulse.net`
- Used as resource prefix: `{environment}-investpulse-*`

**Common environments:**
- `dev` - Automatic deployment from dev branch
- `development` - Manual development environment
- `staging` - Staging environment
- `production` - Production environment

## Integration with GitHub Actions

The scripts are designed to work with GitHub Actions workflows:

```yaml
- name: Build & Prepare Static Assets
  run: ./scripts/build_and_push.sh dev

- name: Deploy Infrastructure with Terraform
  run: ./scripts/deploy.sh dev
```

See `.github/workflows/deploy-dev.yml` for a complete example.

## Troubleshooting

### Permission Errors

Make sure scripts are executable:
```bash
chmod +x scripts/*.sh
```

### Build Failures

1. Check Node.js version: `node --version` (should be 18+)
2. Clear npm cache: `npm cache clean --force`
3. Delete node_modules and reinstall: `rm -rf webapp/node_modules && cd webapp && npm install`

### Terraform Failures

1. Check Terraform version: `terraform version` (should be 1.10+)
2. Verify authentication: `az account show` or check ARM_* environment variables
3. Check Terraform state: `cd infra && terraform state list`

### Network Issues

If you encounter network issues (like Google Fonts failures in build):
1. This is expected in some sandboxed environments
2. The workflows will work in GitHub Actions with proper network access
3. For local testing, you may need to adjust font configurations

## Best Practices

1. **Always test locally first**: Run scripts locally before committing
2. **Use environment-specific configurations**: Different settings for dev/staging/production
3. **Monitor costs**: Keep track of Azure resource usage
4. **Secure secrets**: Never commit sensitive tokens or keys
5. **Version control**: All infrastructure changes should be in version control