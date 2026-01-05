# Finnhub.io API Upstream

This directory contains Azure Functions that act as secure proxy endpoints (upstreams) to the Finnhub.io API. These functions prevent exposing the API key to clients and provide a consistent, cacheable interface for stock market data.

## Architecture

The upstream follows a proxy pattern:
```
Client → Azure Static Web App → Azure Functions (this folder) → Finnhub.io API
```

This is similar to how API gateways like Kong or Nginx configure upstreams, but implemented using Azure Functions for Azure Static Web Apps.

## Available Endpoints

### 1. Stock Quote - `/api/finnhub/quote`
Get real-time stock quote data.

**Request:**
```http
GET /api/finnhub/quote?symbol=AAPL
```

**Response:**
```json
{
  "c": 178.18,  // Current price
  "h": 179.23,  // High price of the day
  "l": 177.26,  // Low price of the day
  "o": 177.74,  // Open price of the day
  "pc": 177.97, // Previous close price
  "t": 1605552332 // Timestamp
}
```

**Cache:** 60 seconds

### 2. Company Profile - `/api/finnhub/profile`
Get company profile information.

**Request:**
```http
GET /api/finnhub/profile?symbol=AAPL
```

**Response:**
```json
{
  "country": "US",
  "currency": "USD",
  "exchange": "NASDAQ",
  "ipo": "1980-12-12",
  "marketCapitalization": 2600000,
  "name": "Apple Inc",
  "phone": "14089961010",
  "shareOutstanding": 16406.4,
  "ticker": "AAPL",
  "weburl": "https://www.apple.com/",
  "logo": "https://static.finnhub.io/logo/...",
  "finnhubIndustry": "Technology"
}
```

**Cache:** 3600 seconds (1 hour)

## Configuration

### Environment Variables
- `FINNHUB_API_KEY` - Your Finnhub.io API key (configured via Terraform in `infra/`)

### Security
- API key is stored securely in Azure Static Web App settings
- Functions use anonymous authentication but hide the API key from clients
- CORS is managed by Azure Static Web Apps
- Rate limiting is handled by Finnhub.io's API limits

## Development

### Local Development
1. Install dependencies:
   ```bash
   cd webapp/api
   npm install
   ```

2. Create `local.settings.json`:
   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "",
       "FUNCTIONS_WORKER_RUNTIME": "node",
       "FINNHUB_API_KEY": "your-api-key-here"
     }
   }
   ```

3. Build and run:
   ```bash
   npm run build
   npm start
   ```

### Testing
Test the endpoints locally:
```bash
curl "http://localhost:7071/api/finnhub/quote?symbol=AAPL"
curl "http://localhost:7071/api/finnhub/profile?symbol=AAPL"
```

## Deployment

The API is automatically deployed with the Static Web App via GitHub Actions. The deployment is configured in `infra/locals.tf`:
- `api_location` points to `/webapp/api`
- `FINNHUB_API_KEY` is injected from Terraform variables

## Infrastructure

The upstream is configured in Terraform:

**variables.tf:**
```hcl
variable "FINNHUB_API_KEY" {
  description = "Finnhub.io API key for stock market data"
  type        = string
  sensitive   = true
}
```

**locals.tf:**
```hcl
app_settings = {
  "api_location" = "/webapp/api"
  "FINNHUB_API_KEY" = var.FINNHUB_API_KEY
}
```

## Adding More Endpoints

To add a new Finnhub endpoint:

1. Create a new TypeScript file in `webapp/api/finnhub/`:
   ```typescript
   // webapp/api/finnhub/news.ts
   import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
   
   export async function news(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
     const symbol = request.query.get("symbol");
     // Implementation...
     return {
       status: 200,
       jsonBody: data,
     };
   }
   
   app.http("news", {
     methods: ["GET"],
     authLevel: "anonymous",
     route: "finnhub/news",
     handler: news,
   });
   ```

2. No function.json needed - Azure Functions v4 uses code-based registration

3. Rebuild and test:
   ```bash
   npm run build
   npm start
   ```

## References

- [Finnhub.io API Documentation](https://finnhub.io/docs/api)
- [Azure Functions Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Azure Static Web Apps API](https://docs.microsoft.com/en-us/azure/static-web-apps/apis)

## Similar Patterns

This upstream configuration is similar to:
- Kong upstream configuration
- Nginx reverse proxy
- Twitter API proxy setup (if one existed in this project)

The pattern provides:
- Security (API key protection)
- Caching
- Rate limiting
- Consistent error handling
- Monitoring and logging
