# Virtual Threads Configuration for InvestPulse Microservices

## Overview

Virtual threads have been enabled across all three InvestPulse microservices (config-server, sentiment-analyzer, and reddit-ingestor). Virtual threads are lightweight threads that dramatically improve scalability and resource efficiency for I/O-bound operations.

### Key Benefits
- **Lower Memory Footprint**: Virtual threads use ~100x less memory than platform threads (~10KB vs ~2MB)
- **Better Resource Utilization**: Handle thousands of concurrent I/O operations without thread pool exhaustion
- **Simplified Concurrency Model**: No need for complex thread pool tuning
- **Improved Throughput**: Better CPU core utilization for I/O-bound workloads

## Configuration

### Spring Boot Properties

Virtual threads are enabled via the following configuration added to each service's `application.yml`:

```yaml
spring:
  threads:
    virtual:
      enabled: true
```

### Web Server (Tomcat) Configuration

For services with HTTP servers (config-server, reddit-ingestor):

```yaml
server:
  tomcat:
    threads:
      virtual:
        enabled: true
```

This enables Tomcat to use virtual threads for handling HTTP requests, providing superior scalability for concurrent requests.

## Implementation Details

### VirtualThreadConfiguration Classes

Each microservice includes a `VirtualThreadConfiguration` class that:
- Detects if virtual threads are enabled via `@ConditionalOnProperty`
- Creates a `VirtualThreadTaskExecutor` for async operations
- Uses spring-managed scheduled/async annotations

#### Config Server
- **Package**: `net.investpulse.configserver.config`
- **File**: `VirtualThreadConfiguration.java`
- **Use Case**: Async config server operations and cloud bus messaging

#### Sentiment Analyzer
- **Package**: `net.investpulse.sentiment.config`
- **File**: `VirtualThreadConfiguration.java`
- **Use Case**: Async Kafka consumption and Parquet file writes

#### Reddit Ingestor
- **Package**: `net.investpulse.reddit.config`
- **File**: `VirtualThreadConfiguration.java`
- **Use Case**: Async HTTP requests to Reddit API and Kafka operations

### How It Works

1. **Spring Boot 3.2+** automatically configures the platform for virtual threads
2. **Tomcat** (when `server.tomcat.threads.virtual.enabled=true`) uses virtual threads for request handling
3. **Custom Executor**: The `VirtualThreadTaskExecutor` bean enables `@Async` and `@Scheduled` methods to run on virtual threads
4. **Kafka Listeners**: Spring Kafka automatically uses the configured task executor for consumer operations

## Behavioral Changes

### Before Virtual Threads
- Fixed thread pool sizes (typically 10-20 threads per pool)
- Thread exhaustion under high load scenarios
- Complex tuning required for different workloads

### After Virtual Threads
- Unbounded virtual thread creation (millions possible)
- No thread pool exhaustion
- Automatic resource management by JVM
- Simpler operational concerns

## Verification

To verify virtual threads are active, check the application logs:

```
Initializing virtual thread task executor for config-server
Initializing virtual thread task executor for sentiment-analyzer
Initializing virtual thread task executor for reddit-ingestor
```

## Performance Monitoring

Monitor these metrics to observe improvements:
- **Thread Count**: Will be very low (10-50) despite high concurrency
- **Memory Usage**: Reduced overall memory consumption
- **Request Latency**: Potentially improved due to better scheduling
- **Throughput**: Higher concurrent request handling capability

## Compatibility Notes

- **Java Version**: Requires Java 21+ (Project uses Java 25)
- **Spring Boot**: Requires Spring Boot 3.2+ (Project uses 3.5.9)
- **Platform Threads Fallback**: If disabled, automatically falls back to traditional platform threads

## Configuration Toggle

To disable virtual threads (e.g., for testing or debugging):

```yaml
spring:
  threads:
    virtual:
      enabled: false
```

The application will automatically use traditional platform threads while maintaining all other functionality.

## References

- [Project Loom - Java Virtual Threads](https://openjdk.org/projects/loom/)
- [Spring Boot Virtual Threads Support](https://spring.io/blog/2024/02/22/spring-boot-3-2-0-released)
- [VirtualThreadTaskExecutor Javadoc](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/core/task/VirtualThreadTaskExecutor.html)
