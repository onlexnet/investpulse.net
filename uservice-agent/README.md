# Purpose

- Interacts (or simulate) buy / sell operations based on algo commands
- Informs algo when requested orderbook positions are done / cancelled
- protects budget
- creates operations raport on demand


## Run

dapr run --app-protocol grpc --app-id abc --app-port 50000 python app.py
