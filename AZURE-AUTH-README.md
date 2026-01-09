# Azure Service Principal Certificate-Based Authentication Setup

## Overview

This document describes the steps taken to configure certificate-based authentication for the Azure service principal `investpulse-net-infra`. This enables secure, automated access to Azure resources without using password-based authentication.

## Service Principal Details

- **Display Name**: `investpulse-net-infra`
- **Application ID**: `bde9a28c-d7c8-4ef5-909b-687263af8675`
- **Tenant ID**: `29084a59-db89-4eb9-908a-53f42318c77d`
- **Subscription**: `dev-investpulse-net` (`ac0e7cdd-3111-4671-a602-0d93afb5df20`)
- **Role Assignment**: Contributor (subscription-wide)

## Purpose

Certificate-based authentication provides several advantages over password-based authentication:

1. **Enhanced Security**: Certificates are more secure than passwords and cannot be easily compromised
2. **No Password Rotation**: Eliminates the need for regular password rotation and management
3. **Audit Trail**: Better tracking of authentication events
4. **Automation-Friendly**: Ideal for CI/CD pipelines and automated deployments
5. **Non-Interactive**: Suitable for background processes and scheduled tasks

## Steps Performed

### 1. Certificate Generation

Created a self-signed X.509 certificate valid for 730 days (2 years):

```bash
mkdir -p ~/.azure/certs

openssl req -x509 \
  -newkey rsa:4096 \
  -keyout ~/.azure/certs/investpulse-net-infra-key.pem \
  -out ~/.azure/certs/investpulse-net-infra-cert.pem \
  -days 730 \
  -nodes \
  -subj "/CN=investpulse-net-infra/O=InvestPulse/C=PL"
```

**Generated files**:
- `investpulse-net-infra-key.pem`: Private key (RSA 4096-bit)
- `investpulse-net-infra-cert.pem`: Public certificate

### 2. Certificate Registration in Azure AD

Registered the public certificate with the Azure AD application:

```bash
az ad app credential reset \
  --id bde9a28c-d7c8-4ef5-909b-687263af8675 \
  --cert @~/.azure/certs/investpulse-net-infra-cert.pem \
  --append
```

This adds the certificate's thumbprint to the service principal's key credentials without removing existing credentials.

### 3. Combined PEM File Creation

Created a single PEM file containing both the private key and certificate for Azure CLI authentication:

```bash
cat ~/.azure/certs/investpulse-net-infra-key.pem \
    ~/.azure/certs/investpulse-net-infra-cert.pem \
    > ~/.azure/certs/investpulse-net-infra-full.pem
```

### 4. PKCS12 Format (Optional)

Created a PKCS12 (.pfx) file for compatibility with other tools:

```bash
openssl pkcs12 -export \
  -out ~/.azure/certs/investpulse-net-infra.pfx \
  -inkey ~/.azure/certs/investpulse-net-infra-key.pem \
  -in ~/.azure/certs/investpulse-net-infra-cert.pem \
  -passout pass:
```

## Usage

### Authenticate with Azure CLI

```bash
az login --service-principal \
  -u bde9a28c-d7c8-4ef5-909b-687263af8675 \
  --certificate ~/.azure/certs/investpulse-net-infra-full.pem \
  --tenant 29084a59-db89-4eb9-908a-53f42318c77d
```

### Verify Authentication

```bash
# Check current account
az account show

# List role assignments
az role assignment list \
  --assignee bde9a28c-d7c8-4ef5-909b-687263af8675 \
  --output table
```

### Example Operations

```bash
# List resource groups
az group list --output table

# List all resources
az resource list --output table

# Create a resource group
az group create --name my-resource-group --location westeurope
```

## Files Created

```
~/.azure/certs/
├── investpulse-net-infra-key.pem      # Private key (KEEP SECURE!)
├── investpulse-net-infra-cert.pem     # Public certificate
├── investpulse-net-infra-full.pem     # Combined file for Azure CLI
└── investpulse-net-infra.pfx          # PKCS12 format (optional)
```

## Security Considerations

### ⚠️ CRITICAL SECURITY NOTES

1. **Private Key Protection**:
   - The private key file (`investpulse-net-infra-key.pem` and `investpulse-net-infra-full.pem`) must be kept secure
   - Never commit these files to version control
   - Set restrictive file permissions: `chmod 600 ~/.azure/certs/*.pem`

2. **Certificate Expiration**:
   - Certificate is valid for 730 days from creation
   - Set a reminder to renew before expiration
   - Check expiration: `openssl x509 -in ~/.azure/certs/investpulse-net-infra-cert.pem -noout -dates`

3. **Access Control**:
   - The service principal has Contributor role on the entire subscription
   - Review and adjust permissions based on the principle of least privilege
   - Consider creating custom roles with specific permissions

4. **Audit and Monitoring**:
   - Monitor service principal activity in Azure Activity Log
   - Set up alerts for suspicious authentication attempts
   - Regularly review role assignments

### Recommended .gitignore Entries

```gitignore
# Azure certificates and credentials
*.pem
*.pfx
*.p12
.azure/certs/
```

## Certificate Renewal

When the certificate approaches expiration:

```bash
# Generate new certificate
openssl req -x509 \
  -newkey rsa:4096 \
  -keyout ~/.azure/certs/investpulse-net-infra-key-new.pem \
  -out ~/.azure/certs/investpulse-net-infra-cert-new.pem \
  -days 730 \
  -nodes \
  -subj "/CN=investpulse-net-infra/O=InvestPulse/C=PL"

# Add new certificate (using --append to keep the old one temporarily)
az ad app credential reset \
  --id bde9a28c-d7c8-4ef5-909b-687263af8675 \
  --cert @~/.azure/certs/investpulse-net-infra-cert-new.pem \
  --append

# Test with new certificate
# If successful, remove old certificate from Azure AD
```

## Troubleshooting

### Authentication Failed

```bash
# Verify certificate is registered
az ad sp show --id bde9a28c-d7c8-4ef5-909b-687263af8675 \
  --query "keyCredentials[].{Type:type,EndDate:endDateTime}" \
  --output table

# Check certificate validity
openssl x509 -in ~/.azure/certs/investpulse-net-infra-cert.pem \
  -noout -dates
```

### Permission Denied

```bash
# List current role assignments
az role assignment list \
  --assignee bde9a28c-d7c8-4ef5-909b-687263af8675 \
  --all \
  --output table
```

## References

- [Azure CLI Service Principal Authentication](https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli)
- [Azure AD Application Certificates](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)
- [OpenSSL Documentation](https://www.openssl.org/docs/)

---

**Last Updated**: December 8, 2025  
**Created By**: Infrastructure Team  
**Service Principal Owner**: InvestPulse Infrastructure Team
