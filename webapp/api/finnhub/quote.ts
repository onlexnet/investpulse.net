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

import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";

export async function quote(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
  context.log("Finnhub quote API proxy called");

  // Get the stock symbol from query parameters
  const symbol = request.query.get("symbol");

  if (!symbol) {
    return {
      status: 400,
      jsonBody: { error: "Missing required parameter: symbol" },
      headers: {
        "Content-Type": "application/json",
      },
    };
  }

  // Get API key from environment variables
  const apiKey = process.env.FINNHUB_API_KEY;

  if (!apiKey) {
    context.error("FINNHUB_API_KEY environment variable not set");
    return {
      status: 500,
      jsonBody: { error: "Server configuration error" },
      headers: {
        "Content-Type": "application/json",
      },
    };
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

    return {
      status: 200,
      jsonBody: data,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=60", // Cache for 1 minute
      },
    };
  } catch (error) {
    context.error("Error fetching from Finnhub API:", error);
    return {
      status: 502,
      jsonBody: {
        error: "Failed to fetch data from Finnhub API",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      headers: {
        "Content-Type": "application/json",
      },
    };
  }
}

app.http("quote", {
  methods: ["GET"],
  authLevel: "anonymous",
  route: "finnhub/quote",
  handler: quote,
});

