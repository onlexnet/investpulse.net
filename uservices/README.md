# InvestPulse Microservices

Event-driven financial sentiment analysis platform for social media (X/Twitter, Reddit).

## Architecture Overview

This project uses a decoupled, event-driven architecture for real-time financial sentiment analysis:

- **`lib-common`**: Shared immutable DTOs (Java Records) for Kafka messages
- **`us-config-server`**: Centralized Spring Cloud Config server (port 9002)
- **`us-reddit`**: Reddit ingestor service - polls subreddits, extracts tickers, routes to Kafka
- **`us-sentiment-analyzer`**: NLP service - consumes from Kafka, performs sentiment analysis, persists to Parquet

### Data Flow

1. **Ingestion**: Reddit ingestor polls subreddits → extracts `$AAPL`, `#TSLA` tickers
2. **Routing**: Dynamic topic router creates/sends to `ticker-{SYMBOL}` Kafka topics
3. **Analysis**: Sentiment analyzer uses financial lexicon-based NLP to score text
4. **Aggregation**: Results published to `sentiment-aggregated` topic for downstream use

## Observability with LGTM Stack

All microservices are instrumented with OpenTelemetry (OTEL) and integrated with the **LGTM stack** (Loki, Grafana, Tempo, Metrics) for full observability.

### What's Instrumented

- **Traces**: Distributed tracing across all services via Tempo (OTLP HTTP on port 4318)
- **Metrics**: Application metrics exported to Tempo via OTLP (10s intervals)
- **Logs**: Structured logs shipped to Loki via OTLP (port 4318) with automatic trace correlation

### Quick Start: Launch LGTM Stack

The LGTM stack runs in docker-compose and is automatically started with the devcontainer:

```bash
# Check LGTM container status
docker ps | grep lgtm

# Restart LGTM if needed
docker-compose -f ../.devcontainer/docker-compose.yaml restart lgtm

# View LGTM logs
docker logs -f lgtm
```

**Grafana Access**: http://localhost:3000
- Username: `admin`
- Password: `admin`

### Viewing Observability Data

#### 1. **Traces (Tempo)**

View distributed traces showing request flow across services:

1. Open Grafana at http://localhost:3000
2. Navigate to **Explore** (compass icon in left sidebar)
3. Select **Tempo** datasource from dropdown
4. Click **Search** tab
5. Filter by:
   - **Service Name**: `sentiment-analyzer`, `reddit-ingestor`, `config-server`
   - **Duration**: `> 100ms` to find slow requests
   - **Status**: `error` to find failed requests
6. Click on any trace to view detailed span timeline

#### 2. **Logs (Loki)**

Query structured logs with trace correlation:

1. Open Grafana at http://localhost:3000
2. Navigate to **Explore**
3. Select **Loki** datasource
4. Example queries:
   ```logql
   # All logs from sentiment-analyzer service
   {service_name="sentiment-analyzer"}
   
   # Error logs only
   {service_name="sentiment-analyzer", level="ERROR"}
   
   # Logs from all services in last 5 minutes
   {service_name=~"sentiment-analyzer|reddit-ingestor|config-server"}
   
   # Search for specific text in logs
   {service_name="reddit-ingestor"} |= "ticker"
   ```
5. Click on **Trace ID** links in logs to jump directly to corresponding trace in Tempo

#### 3. **Metrics (Prometheus)**

View application metrics (JVM, HTTP, Kafka):

1. Open Grafana at http://localhost:3000
2. Navigate to **Explore**
3. Select **Prometheus** datasource
4. Example queries:
   ```promql
   # JVM memory usage
   jvm_memory_used_bytes{application="sentiment-analyzer"}
   
   # HTTP request rate
   rate(http_server_requests_seconds_count[5m])
   
   # Kafka consumer lag
   kafka_consumer_lag{group="sentiment-analyzer-group"}
   ```

### Generating Test Traffic

Use the provided script to generate observability data:

```bash
# Generate 10 iterations with 2s delay (default)
bash scripts/generate-traffic.sh

# Generate 50 iterations with 5s delay
bash scripts/generate-traffic.sh 50 5

# Run continuously until Ctrl+C
bash scripts/generate-traffic.sh infinite 1
```

The script:
- Checks health of all services
- Hits actuator endpoints (health, info, metrics)
- Generates configuration requests to config-server
- Produces traces, logs, and metrics for all services

### Log Correlation with Traces

Logs automatically include `traceId` and `spanId` via OpenTelemetry context propagation:

- **In console logs**: `[traceId=abc123 spanId=def456]`
- **In Loki (OTLP format)**: Trace context automatically attached as resource attributes

To correlate logs with traces:
1. Find a log entry in Loki (it will have trace context automatically)
2. Click the trace ID link (auto-detected by Grafana)
3. View the full distributed trace in Tempo
4. See all related logs from all services for that request

**Benefits of OTLP Logs**:
- Unified protocol for traces, metrics, and logs
- Automatic trace context injection (no manual MDC required)
- Better correlation between signals in Grafana

### Troubleshooting

#### LGTM Not Receiving Data

```bash
# Check LGTM container is running
docker ps | grep lgtm

# Verify LGTM endpoints are accessible
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:4318/v1/traces   # Tempo OTLP (should return 405 Method Not Allowed)

# Check service logs for OTLP export errors
docker logs config-server 2>&1 | grep -i otlp
```

#### Services Can't Connect to LGTM

```bash
# Verify OTLP endpoints from inside devcontainer
curl -I http://lgtm:4318/v1/logs    # Logs OTLP endpoint
curl -I http://lgtm:4318/v1/traces  # Traces OTLP endpoint
curl -I http://lgtm:4318/v1/metrics # Metrics OTLP endpoint

# Check application.yml OTLP configuration
grep -A2 "otlp:" us-*/src/main/resources/application.yml
```

#### No Traces in Tempo

- Ensure `management.tracing.sampling.probability: 1.0` in application.yml
- Check `management.otlp.tracing.endpoint: http://localhost:4318/v1/traces`
- Verify Micrometer dependencies are present (already configured in parent POM)

#### Logs Not Appearing in Loki

- Check OpenTelemetry OTLP appender configuration in logback-spring.xml
- Verify `management.otlp.logging.endpoint: http://localhost:4318/v1/logs` in application.yml
- Check async appender queue isn't full (increase `queueSize` in logback-spring.xml)
- Verify log level is INFO+ (DEBUG/TRACE are filtered out)
- Check service logs for OTLP export errors: `docker logs <service> 2>&1 | grep -i otlp`

## Prerequisites

- Java 25
- Maven (or mvnd for faster builds)
- Kafka running on `localhost:9092`
- PostgreSQL running on `localhost:5432` (for reddit service)
- LGTM stack running via docker-compose (for observability)

## Building the Project

```bash
# Full clean build with tests
mvnd clean install

# Build without tests (faster)
mvnd clean install -DskipTests

# Build specific module
mvnd clean install -pl us-sentiment-analyzer -am
```

## Running Services

### Option 1: Maven (Development)

```bash
# Run config server first (other services depend on it)
mvnd spring-boot:run -pl us-config-server

# Run sentiment analyzer
mvnd spring-boot:run -pl us-sentiment-analyzer

# Run reddit ingestor
mvnd spring-boot:run -pl us-reddit
```

### Option 2: JAR Files (Production-like)

```bash
# Build all services
mvnd clean package -DskipTests

# Run config server
java -jar us-config-server/target/config-server-*.jar

# Run sentiment analyzer
java -jar us-sentiment-analyzer/target/sentiment-analyzer-*.jar

# Run reddit ingestor
java -jar us-reddit/target/reddit-*.jar
```

## Service Ports

| Service              | Port |
|----------------------|------|
| Config Server        | 9002 |
| Sentiment Analyzer   | 9001 |
| Reddit Ingestor      | 9003 |
| Kafka                | 9092 |
| PostgreSQL           | 5432 |
| Schema Registry      | 8081 |
| Grafana (LGTM)       | 3000 |
| OTLP gRPC            | 4317 |
| OTLP HTTP            | 4318 |

## Configuration

Centralized configuration is managed by config-server:
- Config files: `us-config-server/src/main/resources/config/`
- Service-specific: `<service-name>.properties`
- Override with environment variables or local `application.yml`

## Key Features

- **Virtual Threads**: All services use Java 25 virtual threads for high concurrency
- **Event-Driven**: Kafka-based messaging with dynamic topic routing
- **Financial NLP**: Lexicon-based sentiment analysis optimized for financial text
- **Parquet Persistence**: Sentiment data stored in Parquet format for Spark analytics
- **Spring Cloud Bus**: Configuration refresh via Kafka without restarts
- **Error Prone**: Compile-time bug detection with strict checks
- **Checkstyle**: Code quality enforcement with custom rules
- **Full Observability**: OTEL integration with LGTM stack (traces, logs, metrics)

## Data Storage

- **Kafka Topics**: `ticker-{SYMBOL}` for raw posts, `sentiment-aggregated` for results
- **Parquet Files**: `/data/sentiment/ticker={SYMBOL}/year={YYYY}/month={MM}/day={DD}/`
- **PostgreSQL**: Reddit post metadata and deduplication tracking

## Development Tips

- Use `mvnd` instead of `mvn` for parallel builds (10x faster)
- Set `JAVA_HOME` to Java 25 installation
- Configure IDE to use Java 25 and import Error Prone annotations
- Run Kafka and PostgreSQL via docker-compose before starting services
- Check actuator endpoints: `http://localhost:<port>/actuator/health`
- View LGTM observability: `http://localhost:3000`

## License

Copyright © 2026 InvestPulse. All rights reserved.
