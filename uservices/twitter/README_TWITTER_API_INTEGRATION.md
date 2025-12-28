# Twitter API Adapter - Integration Tests

## Overview

The Twitter module now fetches real data from Twitter API v2 using a hexagonal architecture with:
- **Port**: `TweetFetcher` interface
- **Adapter**: `TwitterApiAdapter` implementation using `RestClient`
- **Rate Limiting**: Caffeine-based token bucket (15 requests per 15 minutes)

## Running Integration Tests

Integration tests make real calls to the Twitter API v2. They require valid credentials.

### Prerequisites

1. **Twitter API v2 Bearer Token**
   - Sign up for Twitter Developer Account at https://developer.twitter.com
   - Create an app and generate Bearer Token
   - Note: Free tier allows 500k tweets/month

### Set Environment Variable

```bash
export TWITTER_BEARER_TOKEN="your-bearer-token-here"
```

### Run All Tests (Including Integration)

```bash
mvn test -pl twitter
```

### Run Only Unit Tests (Skip Integration)

```bash
# Unit tests always run - integration tests skip without token
mvn test -pl twitter
```

### Run Only Integration Tests

```bash
mvn test -pl twitter -Dtest=TwitterApiAdapterIntegrationTest
```

## Integration Test Coverage

The `TwitterApiAdapterIntegrationTest` validates:

1. **Real API Connectivity**: Fetches tweets from `@elonmusk` account
2. **Incremental Polling**: Tests `since_id` parameter for fetching only new tweets
3. **Rate Limiting**: Verifies interceptor handles multiple requests correctly
4. **Error Handling**: Tests non-existent user gracefully returns empty list

## Configuration

### Production Config

Located in `config-server/src/main/resources/config/x.properties`:

```properties
twitter.bearer.token=${twitter.bearer.token}  # From Azure Key Vault
twitter.accounts-to-follow=ZeroHedge,charliebilello,elerianm,awealthofcs,OptionsHawk,sentimentrader,stlouisfed,LizAnnSonders,PeterLBrandt
twitter.poll-interval-ms=300000  # 5 minutes
twitter.api.base-url=https://api.twitter.com/2
```

### Local Development Config

Located in `twitter/src/main/resources/application.yml`:

```yaml
spring:
  application:
    name: x
  config:
    import: optional:configserver:http://localhost:8888
  kafka:
    bootstrap-servers: localhost:9092

twitter:
  bearer-token: ${TWITTER_BEARER_TOKEN:}
  api-base-url: https://api.twitter.com/2
```

## Architecture

```
TwitterIngestor (Service Layer)
    ↓ depends on
TweetFetcher (Port Interface)
    ↓ implemented by
TwitterApiAdapter (Infrastructure)
    ↓ uses
RestClient + RateLimitInterceptor
    ↓ calls
Twitter API v2 REST Endpoints
```

## Twitter API v2 Endpoints Used

1. **User Lookup**: `GET /users/by/username/{username}`
   - Returns user ID for username
   
2. **User Tweets**: `GET /users/{userId}/tweets`
   - Query params: `since_id`, `max_results`, `tweet.fields`
   - Returns max 10 tweets per request (configurable)

## Rate Limiting

- **Local Bucket**: 15 requests per 15-minute window (Caffeine cache)
- **Twitter API Limits**: Monitored via response headers
  - `x-rate-limit-remaining`: Remaining requests
  - `x-rate-limit-reset`: Reset timestamp
- **Behavior**: Blocks requests when local bucket exhausted, logs warnings when Twitter limit < 10

## Troubleshooting

### Integration Tests Skipped

```
[WARNING] Tests run: 4, Failures: 0, Errors: 0, Skipped: 4
```

**Solution**: Set `TWITTER_BEARER_TOKEN` environment variable.

### 401 Unauthorized

```
RuntimeException: User lookup failed: 401 UNAUTHORIZED
```

**Solution**: Verify bearer token is valid and not expired.

### 429 Too Many Requests

```
RuntimeException: Twitter API server error: 429 TOO_MANY_REQUESTS
```

**Solution**: Wait for rate limit window to reset. Check `x-rate-limit-reset` header.

### Connection Refused

```
Connection to api.twitter.com refused
```

**Solution**: 
- Check internet connectivity
- Verify `twitter.api.base-url` is correct
- Check if Twitter API is experiencing outages

## Testing Without Real API

For unit tests, `TwitterApiAdapter` is mocked:

```java
@Mock
private TweetFetcher tweetFetcher;

when(tweetFetcher.fetchTweets("testuser", null))
    .thenReturn(List.of(mockTweet));
```

See `TwitterApiAdapterTest` and `TwitterIngestorTest` for examples.

## Further Reading

- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Rate Limits](https://developer.twitter.com/en/docs/twitter-api/rate-limits)
- [Authentication](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens)
