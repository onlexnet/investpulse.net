Regeneracja kodu servera:

python -m grpc_tools.protoc -I../api/grpc --python_out=. --pyi_out=. --grpc_python_out=. app1.proto

## used articles
- https://grpc.io/docs/languages/python/basics/#generating-client-and-server-code
- [Python grpc client and server](https://www.youtube.com/watch?v=WB37L7PjI5k)