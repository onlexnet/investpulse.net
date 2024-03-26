# predictivetrading.net

## Decisions
- use [DAPR multi-app run](https://docs.dapr.io/developing-applications/local-development/multi-app-dapr-run/multi-app-overview/)

## Hints

- [run multiple applications](https://docs.dapr.io/developing-applications/local-development/multi-app-dapr-run/multi-app-overview/)
  ```
  dapr run -f dapr.yaml --resources-path .components
  ```
  
- see local zipking traces:
  ```
  http://localhost:9411
  ```

## used articles
- https://grpc.io/docs/languages/python/basics/#generating-client-and-server-code
- https://adityamattos.com/grpc-in-python-part-3-implementing-grpc-streaming
- [Python grpc client and server](https://www.youtube.com/watch?v=WB37L7PjI5k)

## Known issues
- Zipkin non working in Docker:
  - deinstall zipkin on WSL (host machine)
  - expose port 9411
