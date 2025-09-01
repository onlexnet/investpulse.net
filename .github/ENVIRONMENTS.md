# GitHub Environments Configuration

## Environments Overview

This repository uses GitHub Environments to manage deployments across different stages:

### 1. **Development** (`development`)
- **Trigger**: Push to `develop` branch or manual dispatch
- **URL**: Auto-generated Azure Static Web App URL
- **Purpose**: Development testing and feature validation
- **Protection Rules**: None (fast deployment)

### 2. **Production** (`production`) 
- **Trigger**: Push to `main` branch, releases, or manual dispatch
- **URL**: https://dev.investpulse.net
- **Purpose**: Live production environment
- **Protection Rules**: 
  - Require manual approval (recommended)
  - Restrict to specific users/teams
  - Wait timer (optional)

### 3. **Preview** (`preview-pr-{number}`)
- **Trigger**: Pull Request to `main` or `develop`
- **URL**: Auto-generated per PR
- **Purpose**: Preview changes before merging
- **Cleanup**: Automatic when PR is closed

## Setup Instructions

### Option A: Automatic Setup with Terraform (Recommended)

1. **Configure Terraform variables**:
   ```bash
   cd infra
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your GitHub token and configuration
   ```

2. **Deploy infrastructure and environments**:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

3. **Setup environment secrets**:
   ```bash
   ./scripts/setup-github-secrets.sh
   ```

See [Infrastructure Guide](../infra/GITHUB_ENVIRONMENTS.md) for detailed instructions.

### Option B: Manual Setup

1. Go to repository **Settings** → **Environments**
2. Create the following environments:

#### Development Environment
```
Name: development
Protection rules: None
Secrets:
- AZURE_STATIC_WEB_APPS_API_TOKEN (development app token)
```

#### Production Environment  
```
Name: production
Protection rules:
- Required reviewers: [your-team]
- Wait timer: 5 minutes (optional)
- Restrict to specific branches: main
Secrets:
- AZURE_STATIC_WEB_APPS_API_TOKEN (production app token)
```

### 2. Configure Secrets per Environment

Each environment can have its own secrets:

- **Development**: Development Azure Static Web App token
- **Production**: Production Azure Static Web App token
- **Preview**: Uses same token as development (shared resource)

### 3. Protection Rules (Recommended for Production)

```yaml
Required reviewers:
- Infrastructure team members
- Tech leads

Deployment branches:
- Selected branches: main

Wait timer:
- 5 minutes (allows last-minute checks)
```

## Deployment Workflows

### Automatic Deployments
- **Development**: `develop` branch → `development` environment
- **Production**: `main` branch → `production` environment (with approval)
- **Preview**: Any PR → `preview-pr-{number}` environment

### Manual Deployments
- Use **Actions** tab → **Deploy to Development** → **Run workflow**
- Select environment: `development` or `staging`

## Environment Variables

Each environment can override build-time variables:

```yaml
# Development
NODE_ENV: development
API_BASE_URL: https://api-dev.investpulse.net

# Production  
NODE_ENV: production
API_BASE_URL: https://api.investpulse.net

# Preview
NODE_ENV: preview
API_BASE_URL: https://api-dev.investpulse.net
```

## Security Benefits

1. **Secret Isolation**: Each environment has separate secrets
2. **Access Control**: Different teams can access different environments
3. **Approval Gates**: Production requires manual approval
4. **Audit Trail**: All deployments are logged and trackable
5. **Branch Protection**: Only specific branches can deploy to production

## Monitoring & URLs

| Environment | URL | Monitoring |
|-------------|-----|------------|
| Development | Auto-generated | Basic |
| Production | https://dev.investpulse.net | Full monitoring |
| Preview | Auto-generated per PR | Basic |

## Cleanup

- **Preview environments**: Automatically cleaned up when PR is closed
- **Development**: Manual cleanup if needed
- **Production**: Never auto-cleanup (manual only)

## Troubleshooting

### Common Issues

1. **Missing AZURE_STATIC_WEB_APPS_API_TOKEN**
   - Check environment secrets in Settings → Environments
   - Verify token is for correct Azure resource

2. **Deployment approval not working**
   - Check protection rules are enabled
   - Verify required reviewers have access

3. **Preview not creating**
   - Check PR is targeting `main` or `develop` branch
   - Verify webhook permissions

### Getting Help

- Check **Actions** tab for detailed logs
- Review **Environments** page for deployment history
- Contact infrastructure team for Azure access issues
