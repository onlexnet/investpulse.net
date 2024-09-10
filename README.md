# predictivetrading.net

## Decisions
- use minikube for local hosting to have whole system working on builds based on source files
  - enable [ingress-dns so that we can use services via ingress instead of node ports](https://minikube.sigs.k8s.io/docs/handbook/addons/ingress-dns/)
- use [DAPR multi-app run](https://docs.dapr.io/developing-applications/local-development/multi-app-dapr-run/multi-app-overview/)

## add minikube ingress services to dns
After each restart, when infra-dev is installer, integrate ingress with local DNS so that you can invoke services by its designed dns name

Test
```bash
ping nexus.local # should resolve such address registered in minikube only
```

## Hints

- [how to run multiple applications](https://docs.dapr.io/developing-applications/local-development/multi-app-dapr-run/multi-app-overview/)
  ```
  # metrics port to avoid clash with Prometheus
  dapr run -f dapr.yaml
  ```
  - troubleshooting
    - Error: **Error starting Dapr and app ("scheduler"): fork/exec /home/vscode/.dapr/bin/daprd: no such file or directory**
    - Explanation: I am not sure yet, probably too much jumping between environments with separated DAPR istalaltions and shared DAPR containers
    - Solution:
      ```bash
      dapr uninstall
      dapr init
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
  http://localhost:3000 (user/pass admin/admin)
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
