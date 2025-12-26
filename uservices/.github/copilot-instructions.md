# Copilot Instructions for InvestPulse Microservices

## Big Picture Architecture
This project is a decoupled, event-driven system for financial sentiment analysis on X (Twitter).
- **`common`**: Shared immutable DTOs (Java Records).
- **`twitter` (artifact `x`)**: Ingestor service. Polls X API, extracts tickers, and routes messages to dynamic Kafka topics.
- **`sentiment-analyzer`**: NLP service. Consumes from `ticker-*` topics, performs financial sentiment analysis, and publishes to `sentiment-aggregated`.
- **`config-server`**: Centralized Spring Cloud Config server (port 8888).

## Data Flow Pattern
1. **Ingestion**: `TwitterIngestor` polls accounts -> `TickerExtractor` finds `$AAPL`/`#TSLA`.
2. **Routing**: `DynamicTopicRouter` creates/sends to `ticker-{SYMBOL}` Kafka topics.
3. **Analysis**: `SentimentAggregator` uses `FinancialSentimentService` (lexicon-based) to score text.
4. **Aggregation**: Results published to `sentiment-aggregated` for downstream use.

## Project Conventions
- **Java 25**: Use modern features like Records, Pattern Matching, and `var`.
- **DTOs**: Always use **Java Records** in the `common` module for Kafka messages.
- **Logging**: Use Lombok `@Slf4j`.
- **Kafka**: 
    - Use `ticker-{SYMBOL}` (uppercase) for raw tweet streams.
    - Use `JsonSerializer`/`JsonDeserializer` for message bodies.
- **Configuration**: 
    - Centralized in `config-server/src/main/resources/config/`.
    - Service-specific properties in `x.properties`.

## Critical Workflows
- **Build All**: `mvn clean install` from root.
- **Test Module**: `mvn test -pl <module-name> -am` (e.g., `mvn test -pl twitter -am`).
- **Local Dev**: Ensure Kafka is running on `localhost:9092`.

## Key Files for Reference
- **DTOs**: `common/src/main/java/net/investpulse/common/dto/RawTweet.java`
- **Routing Logic**: `twitter/src/main/java/net/investpulse/x/service/DynamicTopicRouter.java`
- **NLP Logic**: `sentiment-analyzer/src/main/java/net/investpulse/sentiment/service/FinancialSentimentService.java`
