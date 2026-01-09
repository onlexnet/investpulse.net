# Spring Cloud Bus - Event-Driven Config Refresh

## Architecture

This project uses **Spring Cloud Bus** with **Kafka** for event-driven configuration propagation, eliminating the need for polling or scheduled retry.

```
┌──────────────────┐         ┌──────────────┐         ┌──────────────────┐
│  Config Server   │         │    Kafka     │         │ Twitter Service  │
│    (port 9002)   │────────>│ springCloud  │────────>│   (port 8080)    │
│                  │ publish │     Bus      │subscribe│                  │
│  Startup Event   │         │   (topic)    │         │  Auto Refresh!   │
└──────────────────┘         └──────────────┘         └──────────────────┘
```

## How It Works

### 1. Config Server Startup
When Config Server starts:
- `ConfigServerStartupPublisher` detects `ApplicationReadyEvent`
- Publishes `RefreshRemoteApplicationEvent` to Kafka topic `springCloudBus`
- Event contains: origin="config-server", destination="*" (all services)

### 2. Automatic Propagation
- Kafka distributes event to all subscribed microservices
- No polling, no scheduled retry - pure event-driven

### 3. Service Auto-Refresh
When Twitter service receives the event:
- `ConfigServerEventListener` logs the event
- Spring Cloud Bus automatically triggers configuration refresh
- `@RefreshScope` beans are recreated with new config values
- Application seamlessly picks up Config Server configuration

## Benefits Over Retry/Polling

| Approach | Latency | Network Load | Complexity |
|----------|---------|--------------|------------|
| **Scheduled Retry** | 1-5 minutes | High (constant polling) | Medium |
| **Spring Cloud Bus** | < 1 second | Minimal (event-only) | Low |

## Configuration

### Config Server
```yaml
spring:
  cloud:
    bus:
      enabled: true
      destination: springCloudBus
  kafka:
    bootstrap-servers: localhost:9092

management:
  endpoints:
    web:
      exposure:
        include: busrefresh,health,info
```

### Twitter Service
```yaml
spring:
  cloud:
    bus:
      enabled: true
      destination: springCloudBus
      refresh:
        enabled: true  # Auto-refresh on bus events
  kafka:
    bootstrap-servers: localhost:9092

management:
  endpoints:
    web:
      exposure:
        include: busrefresh,refresh,health,info
```

## Manual Refresh Trigger

You can also manually trigger a refresh from Config Server to all services:

```bash
# Refresh all services
curl -X POST http://localhost:9002/actuator/busrefresh

# Refresh specific service
curl -X POST http://localhost:9002/actuator/busrefresh/x
```

## Testing the Flow

1. **Start Kafka** (if not running):
   ```bash
   docker-compose up -d kafka
   ```

2. **Start Twitter service first** (before Config Server):
   ```bash
   mvn spring-boot:run -pl twitter
   ```
   - Service starts with local configuration (port 8080)
   - Waits for Config Server event

3. **Start Reddit service** (in another terminal):
   ```bash
   mvn spring-boot:run -pl reddit
   ```
   - Service starts with local configuration (port 9003)
   - Waits for Config Server event
   - Monitors configured subreddits for ticker mentions

4. **Start Config Server** (in another terminal):
   ```bash
   mvn spring-boot:run -pl config-server
   ```
   - Publishes startup event to Kafka (port 9002)
   - All services automatically refresh within seconds!

5. **Start Sentiment Analyzer** (optional, in another terminal):
   ```bash
   mvn spring-boot:run -pl sentiment-analyzer
   ```
   - Consumes from `ticker-*` topics
   - Performs NLP sentiment analysis
   - Publishes results to `sentiment-aggregated` topic

6. **Check logs** in any service:
   ```
   INFO  ConfigServerEventListener - Received configuration refresh event from Config Server
   INFO  ConfigServerEventListener - Event details - Origin: config-server, Destination: *
   INFO  ConfigServerEventListener - Configuration successfully synchronized with Config Server
   ```

## Components

### Config Server
- **ConfigServerStartupPublisher**: Publishes event when Config Server is ready

### Twitter Service (x)
- **ConfigServerEventListener**: Listens for refresh events from Kafka
- **TwitterRawProps** (@RefreshScope): Automatically reloaded on bus events
- **TwitterIngestor**: Polls Twitter API for configured accounts
- **DynamicTopicRouter**: Routes tweets to `ticker-{SYMBOL}` topics

### Reddit Service
- **ConfigServerEventListener**: Listens for refresh events from Kafka
- **RedditIngestorScheduler** (@Scheduled): Periodically ingests Reddit posts
- **RedditIngestor**: Fetches posts from configured subreddits
- **RedditSentimentService**: Analyzes financial sentiment using Loughran-McDonald lexicon
- **PostDeduplicationCache**: Prevents duplicate post processing

### Sentiment Analyzer
- **ConfigServerEventListener**: Listens for refresh events from Kafka
- **SentimentAggregator**: Consumes from `ticker-*` topics and performs NLP analysis
- **FinancialSentimentService**: Scores text sentiment
- **ParquetSentimentWriter**: Persists results to Parquet files for analytics

## Fallback Strategy

The system still maintains:
- `optional:configserver:` - service works without Config Server
- Startup retry (10 attempts) - tries to connect during initial boot
- Event-driven refresh - picks up Config Server when it becomes available

This gives you the best of both worlds: resilient startup + instant synchronization.
