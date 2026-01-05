/**
 * Azure Function: Finnhub Company Profile API Proxy
 * 
 * This function retrieves company profile information from Finnhub.io
 * 
 * Endpoint: /api/finnhub/profile?symbol=AAPL
 * 
 * @see https://finnhub.io/docs/api/company-profile2
 */

import { AzureFunction, Context, HttpRequest } from "@azure/functions";

const httpTrigger: AzureFunction = async function (
  context: Context,
  req: HttpRequest
): Promise<void> {
  context.log("Finnhub company profile API proxy called");

  const symbol = req.query.symbol;

  if (!symbol) {
    context.res = {
      status: 400,
      body: { error: "Missing required parameter: symbol" },
      headers: {
        "Content-Type": "application/json",
      },
    };
    return;
  }

  const apiKey = process.env.FINNHUB_API_KEY;

  if (!apiKey) {
    context.log.error("FINNHUB_API_KEY environment variable not set");
    context.res = {
      status: 500,
      body: { error: "Server configuration error" },
      headers: {
        "Content-Type": "application/json",
      },
    };
    return;
  }

  try {
    const finnhubUrl = `https://finnhub.io/api/v1/stock/profile2?symbol=${encodeURIComponent(
      symbol
    )}&token=${apiKey}`;

    const response = await fetch(finnhubUrl);

    if (!response.ok) {
      throw new Error(`Finnhub API returned status ${response.status}`);
    }

    const data = await response.json();

    context.res = {
      status: 200,
      body: data,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=3600", // Cache for 1 hour
      },
    };
  } catch (error) {
    context.log.error("Error fetching from Finnhub API:", error);
    context.res = {
      status: 502,
      body: {
        error: "Failed to fetch data from Finnhub API",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      headers: {
        "Content-Type": "application/json",
      },
    };
  }
};

export default httpTrigger;
