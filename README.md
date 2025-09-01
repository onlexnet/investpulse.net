# investpulse.net

Financial analytics dashboard application with microservices architecture.

## Architecture

- **Frontend**: Next.js 15 React application (`webapp/`) - deployed as static site
- **Backend**: Microservices in Java/Python (`try/`) - **AI agents should ignore this folder**
- **Infrastructure**: Azure resources managed by Terraform (`infra/`)

## Quick Start

### Frontend Development

```bash
cd webapp
npm install
npm run dev -- -p 8080  # Runs on port 8080 (default 3000)
```

### Static Build & Deploy

```bash
cd webapp
npm run build:static  # Generates static files in `out/` folder
```

### Infrastructure Deployment

```bash
cd infra
terraform init
terraform plan
terraform apply
```

## Deployment

- **Static Web App**: Automatically deployed via GitHub Actions to Azure Static Web Apps
- **Domain**: `dev.investpulse.net`
- **Cost**: Free tier ($0/month)

## Decisions

- Use [devcontainers/vscode](https://containers.dev/guide/dockerfile) as main dev tool
- Static site deployment for zero-cost hosting
- Azure Static Web Apps for CI/CD integration

