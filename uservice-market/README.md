# Scope
- Distribute locally in real time changes on the market

# Run tests
```
pytest -v
```

## run standalone
dapr run --app-protocol grpc --app-port 50052 --app-id market python app.py

## used articles
- [gRpc interceptors](https://adityamattos.com/grpc-in-python-part-4-interceptors)
- https://grpc.io/docs/languages/python/basics/#generating-client-and-server-code
- [Python grpc client and server](https://www.youtube.com/watch?v=WB37L7PjI5k)