# Purpose

- Interacts (or simulate) buy / sell operations based on algo commands
- Informs algo when requested orderbook positions are done / cancelled
- protects budget
- creates operations raport on demand

## Run

run the app for local testing
```
dapr run --resources-path ../.components --app-protocol grpc --app-id app1 --app-port 50000 python app.py
```

Send an event to the app for local testing
```
dapr publish --publish-app-id app1 --pubsub pubsub --topic onlexnet:v1:onlexnet.pdt.market.events.MarketChangedEvent --data '{"orderId": "100"}'
```