# Single Environment Infrastructure with envName

This configuration creates infrastructure for a single environment using the `envName` variable as a prefix for all resource names.

## What Gets Created

When you set `envName = "dev1"`, the following resources are created:

### Azure Resources
- **Resource Group**: `dev1-investpulse-rg`
- **Static Web App**: `dev1-investpulse-webapp`
- **Custom Domain**: `dev1.investpulse.net`

### GitHub Environment
- **Environment Name**: `dev1`
- **Wait Timer**: 0 minutes (5 minutes if envName contains "prod" or "production")

### DNS Record (Cloudflare)
- **DNS Record**: `dev1.investpulse.net` → Azure Static Web App

## Usage Examples

### Example 1: Development Environment
```hcl
# terraform.tfvars
envName = "dev1"
```
**Result:**
- Resource Group: `dev1-investpulse-rg`
- Static Web App: `dev1-investpulse-webapp`
- URL: `https://dev1.investpulse.net`
- GitHub Environment: `dev1`

### Example 2: Staging Environment
```hcl
# terraform.tfvars
envName = "staging"
```
**Result:**
- Resource Group: `staging-investpulse-rg`
- Static Web App: `staging-investpulse-webapp`
- URL: `https://staging.investpulse.net`
- GitHub Environment: `staging`

### Example 3: Production Environment
```hcl
# terraform.tfvars
envName = "production"
```
**Result:**
- Resource Group: `production-investpulse-rg`
- Static Web App: `production-investpulse-webapp`
- URL: `https://production.investpulse.net`
- GitHub Environment: `production` (with 5-minute wait timer)

## Key Benefits

1. **Consistent Naming**: All resources use the same prefix pattern
2. **Single Variable**: Only need to change `envName` to create different environments
3. **Clean Separation**: Each environment gets its own resource group
4. **DNS Automation**: Subdomain automatically created based on environment name
5. **GitHub Integration**: Environment name matches exactly in GitHub

## Environment Variables

The configuration uses these local values based on `envName`:

```hcl
locals {
  resource_group_name   = "${var.envName}-investpulse-rg"
  static_web_app_name   = "${var.envName}-investpulse-webapp"
  custom_domain         = "${var.envName}.${var.base_domain}"
}
```

## Deployment Process

1. **Set Environment Name**:
   ```hcl
   # terraform.tfvars
   envName = "your-env-name"
   ```

2. **Deploy Infrastructure**:
   ```bash
   terraform plan
   terraform apply
   ```

3. **Configure GitHub Secrets**:
   - Go to: `https://github.com/onlexnet/investpulse.net/settings/environments/{envName}`
   - Add secret: `AZURE_STATIC_WEB_APPS_API_TOKEN`

4. **Access Your App**:
   - URL: `https://{envName}.investpulse.net`

## Multiple Environments

To deploy multiple environments, use different values for `envName`:

```bash
# Deploy dev1
terraform apply -var="envName=dev1"

# Deploy staging  
terraform apply -var="envName=staging"

# Deploy production
terraform apply -var="envName=production"
```

Or use Terraform workspaces:

```bash
terraform workspace new dev1
terraform apply -var="envName=dev1"

terraform workspace new staging
terraform apply -var="envName=staging"
```

## Environment Name Rules

- Must contain only lowercase letters, numbers, and hyphens
- Used as subdomain: `{envName}.investpulse.net`
- Used as resource prefix: `{envName}-investpulse-*`
- Used as GitHub environment name: `{envName}`

## Special Production Behavior

If `envName` contains "prod" or "production":
- GitHub environment gets a 5-minute wait timer
- Can be used for additional production-specific configurations

This approach provides maximum flexibility while maintaining consistent naming across all resources.
