# InvestPulse Infrastructure

This Terraform configuration creates a single environment infrastructure for the InvestPulse web application using Azure Static Web Apps, GitHub Environments, and Cloudflare DNS.

## Architecture

The infrastructure is designed around a single `envName` variable that drives:
- **Resource Group**: `investpulse-{envName}-rg`
- **Static Web App**: `investpulse-{envName}-webapp`
- **Custom Domain**: 
  - Production: `investpulse.net`
  - Other environments: `{envName}.investpulse.net`
- **GitHub Environment**: `{envName}`
- **DNS Record**: Points to Azure Static Web App

## Quick Start

### 1. Set Environment Name

Edit `terraform.tfvars`:
```hcl
envName = "development"  # or "production", "staging", etc.
```

### 2. Configure Secrets

Create `secret.auto.tfvars`:
```hcl
github_token         = "ghp_your_github_token"
cloudflare_api_token = "your_cloudflare_token"
```

### 3. Deploy Infrastructure

```bash
terraform init
terraform plan
terraform apply
```

## Environment Examples

### Development Environment
```hcl
envName = "development"
```
Creates:
- Resource Group: `investpulse-development-rg`
- Static Web App: `investpulse-development-webapp`
- Domain: `development.investpulse.net`
- GitHub Environment: `development`

### Production Environment
```hcl
envName = "production" 
```
Creates:
- Resource Group: `investpulse-production-rg`
- Static Web App: `investpulse-production-webapp`
- Domain: `investpulse.net` (root domain)
- GitHub Environment: `production` (with 5-minute wait timer)

### Staging Environment
```hcl
envName = "staging"
```
Creates:
- Resource Group: `investpulse-staging-rg`
- Static Web App: `investpulse-staging-webapp`
- Domain: `staging.investpulse.net`
- GitHub Environment: `staging`

## Variables

| Variable | Description | Type | Default |
|----------|-------------|------|---------|
| `envName` | Environment name that drives all resource naming | `string` | **Required** |
| `subscription_id` | Azure subscription ID | `string` | `"ac0e7cdd-3111-4671-a602-0d93afb5df20"` |
| `location` | Azure region for resources | `string` | `"westeurope"` |
| `base_domain` | Base domain for DNS entries | `string` | `"investpulse.net"` |
| `github_owner` | GitHub repository owner/organization | `string` | `"onlexnet"` |
| `github_repository` | GitHub repository name | `string` | **Required** |
| `github_token` | GitHub Personal Access Token | `string` | **Required** (sensitive) |
| `cloudflare_api_token` | Cloudflare API token for DNS | `string` | **Required** (sensitive) |
| `cloudflare_zone_id` | Cloudflare Zone ID | `string` | `"2fa34bc4e1284682e9047b76b5826ffd"` |

## Outputs

After deployment, important information is provided:

- `environment_info`: Environment configuration details
- `domain_info`: Domain and DNS configuration  
- `azure_static_web_app_info`: Azure Static Web App details
- `resource_group_info`: Resource group details
- `deployment_instructions`: Step-by-step deployment guide

## Post-Deployment Setup

### 1. Configure GitHub Environment Secrets

1. Get the Azure Static Web App deployment token:
   ```bash
   # From Azure Portal > Static Web App > Manage deployment token
   ```

2. Add to GitHub Environment:
   - Go to: `https://github.com/{owner}/{repo}/settings/environments/{envName}`
   - Add secret: `AZURE_STATIC_WEB_APPS_API_TOKEN`

### 2. Deploy Application

Use GitHub Actions targeting the specific environment:
```yaml
- name: Deploy to Azure Static Web Apps
  uses: Azure/static-web-apps-deploy@v1
  with:
    azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
    repo_token: ${{ secrets.GITHUB_TOKEN }}
    action: "upload"
    app_location: "/webapp"
    output_location: "out"
```

## DNS Configuration

### Automatic (with Cloudflare)
If `cloudflare_api_token` and `cloudflare_zone_id` are configured, DNS records are created automatically.

### Manual
If Cloudflare is not configured, manually create a CNAME record:
- **Name**: `{envName}` (or `@` for production)
- **Type**: `CNAME`
- **Value**: `{static_web_app_default_hostname}` (from outputs)

## Cost Optimization

- **Azure Static Web App (Free Tier)**: $0/month
  - 0.5 GB bandwidth
  - Up to 2 custom domains
  - No API/functions support
- **Resource Group**: Free
- **GitHub Environments**: Free (on public repos)
- **Cloudflare DNS**: Free

**Total Cost**: $0/month for typical development workloads

## Multiple Environments

To deploy multiple environments, use Terraform workspaces or separate directories:

### Option 1: Terraform Workspaces
```bash
# Create development environment
terraform workspace new development
terraform apply -var="envName=development"

# Create production environment  
terraform workspace new production
terraform apply -var="envName=production"
```

### Option 2: Separate Directories
```
infra/
├── environments/
│   ├── development/
│   │   ├── main.tf -> ../../main.tf
│   │   ├── variables.tf -> ../../variables.tf
│   │   └── terraform.tfvars (envName = "development")
│   └── production/
│       ├── main.tf -> ../../main.tf
│       ├── variables.tf -> ../../variables.tf
│       └── terraform.tfvars (envName = "production")
```

## Security Best Practices

1. **Never commit secrets** to version control
2. **Use environment variables** for sensitive values:
   ```bash
   export TF_VAR_github_token="ghp_your_token"
   export TF_VAR_cloudflare_api_token="your_token"
   ```
3. **Restrict GitHub token permissions** to minimum required
4. **Use separate Cloudflare tokens** per environment if possible
5. **Enable Terraform state locking** with Azure Storage

## Troubleshooting

### Common Issues

1. **GitHub Environment creation fails**
   - Ensure GitHub token has `admin:org` permissions
   - Verify repository exists and is accessible

2. **DNS not resolving**
   - Check Cloudflare zone ID is correct
   - Verify API token has DNS edit permissions
   - Allow time for DNS propagation (up to 24 hours)

3. **Static Web App deployment fails**
   - Verify deployment token is correct
   - Check GitHub Actions logs
   - Ensure app_location and output_location are correct

### Getting Help

- Check Terraform plan output before applying
- Review Azure Portal for resource status
- Check GitHub Actions deployment logs
- Verify DNS settings in Cloudflare dashboard

## Contributing

1. Follow Terraform best practices
2. Update documentation for any changes
3. Test with `terraform plan` before committing
4. Use conventional commit messages

### Variables used in terraform cloud:
- TF_VAR_CLOUDFLARE_API_TOKEN
  - Cloudflare token named investpulse-dns-edit to update DNS records in investpulse.net
  - Generate at: https://dash.cloudflare.com/profile/api-tokens
  - Required permissions: Zone:Zone:Read, Zone:DNS:Edit for investpulse.net zone
- TF_VAR_GITHUB_TOKEN
  - GitHub Personal Access Token
  - Generate at: https://github.com/settings/tokens
  - Required permissions: repo, admin:repo_hook
- ARM_CLIENT_ID, ARM_CLIENT_SECRET, ARM_SUBSCRIPTION_ID, ARM_TENANT_ID:
  - Azure Service Principal credentials for Terraform to manage Azure resources
  - Create with: `az ad sp create-for-rbac --name investpulse-net-infra --role contributor --scopes /subscriptions/ac0e7cdd-3111-4671-a602-0d93afb5df20`
  - More info: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/service_principal_client_secret
