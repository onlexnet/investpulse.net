# predictivetrading.net

## Decisions
- use [DAPR multi-app run](https://docs.dapr.io/developing-applications/local-development/multi-app-dapr-run/multi-app-overview/)

## Hints

- [run multiple applications](https://docs.dapr.io/developing-applications/local-development/multi-app-dapr-run/multi-app-overview/)
  ```
  # metrics port to avoid clash with Prometheus
  dapr run -f dapr.yaml
  ```
  
- see local zipking traces:
  ```
  http://localhost:9411
  ```

- see kibana dashboard:
  ```
  # run dockerized monitoring
  cd infra
  docker compose up -d
  # see results
  http://localhost:3000
  ```

- run monitoring
  - enable metrics in dapr:
    Metrics endpoint is open by default
    more: https://v1-10.docs.dapr.io/operations/monitoring/metrics/metrics-overview/

## used articles
- https://grpc.io/docs/languages/python/basics/#generating-client-and-server-code
- https://adityamattos.com/grpc-in-python-part-3-implementing-grpc-streaming
- [Python grpc client and server](https://www.youtube.com/watch?v=WB37L7PjI5k)
- [Python async grpc](https://realpython.com/python-microservices-grpc/#asyncio-and-grpc)

## Known issues
- AVRO deserialization in Python does not work when you import more than one module
  - it orerrides internal globbal variable so that some definitions of serializers disappeared
    schema_classes:
    ```python
    __SCHEMA_TYPES = {
        'onlexnet.pdt.market.events.MarketChangedEvent': MarketChangedEventClass,
        'MarketChangedEvent': MarketChangedEventClass,
    }

    _json_converter = avrojson.AvroJsonConverter(use_logical_types=False, schema_types=__SCHEMA_TYPES)
    avrojson.set_global_json_converter(_json_converter)
    ```
  - solution:
    use
    market_events.MarketChangedEvent._construct
    instead of 
    market_events.MarketChangedEvent.from_obj
