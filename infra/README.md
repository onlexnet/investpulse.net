# Infrastructure

This folder contains Terraform configuration for deploying the InvestPulse web application infrastructure on Azure and GitHub.

## Architecture

[Architecture details](../docs/arch/README.md)

## Components

- **Azure Static Web App**: Hosts the React/Next.js application from `/webapp` folder
- **Resource Group**: Container for all Azure resources
- **Custom Domain**: Configuration for `dev.investpulse.net`
- **GitHub Environments**: Automated creation of development and production environments
- **Protection Rules**: Manual approval gates for production deployments

## Quick Start

### 1. Prerequisites
```bash
# Install tools
terraform --version  # >= 1.10
az --version         # Azure CLI
gh --version         # GitHub CLI

# Authenticate
az login
gh auth login
```

### 2. Configure & Deploy
```bash
# Setup configuration
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your GitHub token and settings

# Deploy infrastructure
terraform init
terraform plan
terraform apply

# Setup GitHub secrets
./scripts/setup-github-secrets.sh
```

See [GitHub Environments Guide](./GITHUB_ENVIRONMENTS.md) for detailed instructions.

## Deployment

### Prerequisites

1. Azure CLI installed and logged in
2. Terraform installed (>= 1.10)
3. Access to Azure subscription: `ac0e7cdd-3111-4671-a602-0d93afb5df20`

### Deploy Infrastructure

```bash
cd infra
terraform init
terraform plan
terraform apply
```

### Deploy Web Application

The web application from `/webapp` folder is automatically deployed via GitHub Actions using **GitHub Environments**:

#### Environments
- **Development**: Auto-deploy from `develop` branch
- **Production**: Auto-deploy from `main` branch (with approval)
- **Preview**: Auto-deploy from Pull Requests

#### Setup GitHub Environments
1. Go to repository **Settings** → **Environments**
2. Create environments: `development`, `production`
3. Configure protection rules for production (manual approval)
4. Add `AZURE_STATIC_WEB_APPS_API_TOKEN` secret to each environment

See [GitHub Environments Configuration](../.github/ENVIRONMENTS.md) for detailed setup.

**Manual deployment steps:**

1. Build the static app:
   ```bash
   cd webapp
   npm install
   npm run build:static
   ```

2. The built files will be in `webapp/out/` directory

3. Upload to Azure Static Web App using Azure CLI or GitHub Actions

### Configuration

- **Static Web App settings**:
  - App location: `/webapp`
  - Build command: `npm run build:static`
  - Output location: `out`
  - No API backend

### Secrets Required

Add the following secrets to **GitHub Environments** (not repository-wide):

#### Development Environment
- `AZURE_STATIC_WEB_APPS_API_TOKEN`: Development app deployment token

#### Production Environment  
- `AZURE_STATIC_WEB_APPS_API_TOKEN`: Production app deployment token

Get tokens from: Azure Portal > Static Web App > Manage deployment token

## Cost Estimation

- Azure Static Web App (Free tier): **$0 USD/month**
- Resource Group: **Free**
- Custom Domain: **Included** (up to 2 domains)

**Total**: $0 USD/month

### Free Tier Limitations
- 0.5 GB bandwidth per month
- Up to 2 custom domains
- No APIs/functions support
- Basic authentication only