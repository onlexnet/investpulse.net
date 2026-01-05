/**
 * Azure Function: Finnhub Quote API Proxy
 * 
 * This function acts as a secure proxy to the Finnhub.io API for stock quotes.
 * It prevents exposing the API key to the client and provides a consistent interface.
 * 
 * Endpoint: /api/finnhub/quote?symbol=AAPL
 * 
 * @see https://finnhub.io/docs/api/quote
 */

import { AzureFunction, Context, HttpRequest } from "@azure/functions";

const httpTrigger: AzureFunction = async function (
  context: Context,
  req: HttpRequest
): Promise<void> {
  context.log("Finnhub quote API proxy called");

  // Get the stock symbol from query parameters
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

  // Get API key from environment variables
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
    // Make request to Finnhub API
    const finnhubUrl = `https://finnhub.io/api/v1/quote?symbol=${encodeURIComponent(
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
        "Cache-Control": "public, max-age=60", // Cache for 1 minute
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
