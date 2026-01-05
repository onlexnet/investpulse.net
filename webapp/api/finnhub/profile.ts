/**
 * Azure Function: Finnhub Company Profile API Proxy
 * 
 * This function retrieves company profile information from Finnhub.io
 * 
 * Endpoint: /api/finnhub/profile?symbol=AAPL
 * 
 * @see https://finnhub.io/docs/api/company-profile2
 */

import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";

export async function profile(request: HttpRequest, context: InvocationContext): Promise<HttpResponseInit> {
  context.log("Finnhub company profile API proxy called");

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
    const finnhubUrl = `https://finnhub.io/api/v1/stock/profile2?symbol=${encodeURIComponent(
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
        "Cache-Control": "public, max-age=3600", // Cache for 1 hour
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

app.http("profile", {
  methods: ["GET"],
  authLevel: "anonymous",
  route: "finnhub/profile",
  handler: profile,
});

