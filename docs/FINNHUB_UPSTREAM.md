# Finnhub.io Upstream Integration

## Overview

This document describes the Finnhub.io upstream integration for the InvestPulse application. The integration follows an API Gateway/upstream pattern commonly used in microservices architectures.

## What is an "Upstream"?

In API Gateway terminology (Kong, Nginx, etc.), an "upstream" is a backend service that the gateway proxies requests to. The gateway acts as a secure intermediary that:
- Hides backend API credentials from clients
- Provides caching and rate limiting
- Offers consistent error handling
- Enables monitoring and logging

## Architecture

### Request Flow
```
Client Browser
    ↓
Azure Static Web App (Frontend)
    ↓
Azure Functions (API Proxy/Upstream)
    ↓
Finnhub.io API (External Service)
```

### Components

1. **Frontend (webapp/)**: Next.js application that makes API calls to `/api/finnhub/*`
2. **API Proxy (webapp/api/)**: Azure Functions that forward requests to Finnhub.io
3. **Infrastructure (infra/)**: Terraform configuration for deployment and secrets management
4. **External Service**: Finnhub.io stock market data API

## Comparison to Traditional Upstreams

### Kong API Gateway Example
```yaml
upstreams:
  - name: finnhub-upstream
    targets:
      - target: finnhub.io:443
        weight: 100
    
services:
  - name: finnhub-service
    url: https://finnhub.io/api/v1
    routes:
      - name: quote-route
        paths:
          - /api/finnhub/quote
```

### Our Azure Implementation
```typescript
// webapp/api/finnhub/quote.ts
const finnhubUrl = `https://finnhub.io/api/v1/quote?symbol=${symbol}&token=${apiKey}`;
const response = await fetch(finnhubUrl);
```

Both approaches achieve the same goal: secure proxying to an external API.

## Features

### Security
- **API Key Protection**: Finnhub API key never exposed to clients
- **Environment Variables**: Secure key storage via Azure settings
- **Anonymous Auth**: Public endpoints with backend security

### Performance
- **Caching**: Response caching at the proxy layer
  - Quote data: 60 seconds
  - Profile data: 3600 seconds (1 hour)
- **CDN**: Azure Static Web Apps' built-in CDN

### Reliability
- **Error Handling**: Consistent error responses
- **Logging**: Azure Functions logging and monitoring
- **Retry Logic**: Can be added at the proxy layer

## Configuration

### Terraform Variables
```hcl
# infra/variables.tf
variable "FINNHUB_API_KEY" {
  description = "Finnhub.io API key for stock market data"
  type        = string
  sensitive   = true
}
```

### App Settings
```hcl
# infra/locals.tf
app_settings = {
  "api_location"    = "/webapp/api"
  "FINNHUB_API_KEY" = var.FINNHUB_API_KEY
}
```

### GitHub Secrets
The Finnhub API key is stored as a GitHub environment secret and injected during Terraform apply:
```
GitHub Repo → Settings → Environments → {envName} → FINNHUB_API_KEY
```

## Available Endpoints

### 1. Stock Quote
```http
GET /api/finnhub/quote?symbol=AAPL

Response:
{
  "c": 178.18,   // Current price
  "h": 179.23,   // High
  "l": 177.26,   // Low
  "o": 177.74,   // Open
  "pc": 177.97   // Previous close
}
```

### 2. Company Profile
```http
GET /api/finnhub/profile?symbol=AAPL

Response:
{
  "name": "Apple Inc",
  "ticker": "AAPL",
  "exchange": "NASDAQ",
  "country": "US",
  "marketCapitalization": 2600000,
  ...
}
```

## Usage Example

### Frontend Code
```typescript
// webapp/src/lib/finnhub.ts
export async function getStockQuote(symbol: string) {
  const response = await fetch(`/api/finnhub/quote?symbol=${symbol}`);
  if (!response.ok) {
    throw new Error('Failed to fetch stock quote');
  }
  return response.json();
}

export async function getCompanyProfile(symbol: string) {
  const response = await fetch(`/api/finnhub/profile?symbol=${symbol}`);
  if (!response.ok) {
    throw new Error('Failed to fetch company profile');
  }
  return response.json();
}
```

### Component Usage
```typescript
// webapp/src/components/StockCard.tsx
import { useEffect, useState } from 'react';
import { getStockQuote } from '@/lib/finnhub';

export function StockCard({ symbol }: { symbol: string }) {
  const [quote, setQuote] = useState(null);
  
  useEffect(() => {
    getStockQuote(symbol).then(setQuote);
  }, [symbol]);
  
  return (
    <div>
      <h2>{symbol}</h2>
      <p>Price: ${quote?.c}</p>
    </div>
  );
}
```

## Development

### Local Testing
```bash
# Start the API locally
cd webapp/api
npm install
npm run build
npm start

# Test endpoints
curl "http://localhost:7071/api/finnhub/quote?symbol=AAPL"
curl "http://localhost:7071/api/finnhub/profile?symbol=AAPL"
```

### Deployment
The API is automatically deployed with the Static Web App via GitHub Actions. No separate deployment is needed.

## Extending the Upstream

To add more Finnhub endpoints:

1. Create a new function file: `webapp/api/finnhub/news.ts`
2. Add corresponding `function.json`
3. Rebuild and test
4. Deploy via GitHub Actions

## Rate Limits

Finnhub.io free tier limits:
- 60 API calls/minute
- 30 API calls/second

Consider implementing rate limiting at the proxy layer if needed.

## Monitoring

Azure Functions provides:
- Request logs
- Performance metrics
- Error tracking
- Application Insights integration

Access logs via:
```bash
func azure functionapp logstream <function-app-name>
```

## Similar Patterns

This implementation is similar to:
- **Twitter API Proxy**: If you were to proxy Twitter API, the pattern would be identical
- **Kong Upstream**: Similar concept but using API Gateway
- **Nginx Proxy Pass**: Similar to nginx reverse proxy configuration
- **AWS API Gateway**: Similar to AWS API Gateway integration

## Benefits

1. **Security**: API keys never exposed to clients
2. **Flexibility**: Easy to switch providers or add caching
3. **Monitoring**: Centralized logging and metrics
4. **Cost Control**: Can implement rate limiting and caching
5. **Consistency**: Single API interface regardless of backend changes

## References

- [Finnhub.io API Docs](https://finnhub.io/docs/api)
- [Azure Functions HTTP Trigger](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger)
- [Azure Static Web Apps API](https://docs.microsoft.com/en-us/azure/static-web-apps/apis)
- [API Gateway Pattern](https://microservices.io/patterns/apigateway.html)
