# Scope
Service designed to create SELL/BUY signals

# Details
It uses [Technical Analysis Library in Python](https://pypi.org/project/ta/)
ta==0.11.0

## Run and test

Run by:
dapr run --app-protocol grpc --app-port 50054 --app-id scheduler --resources-path ../.components python app.py

Send a message:
dapr publish --publish-app-id scheduler --pubsub pubsub --topic onlexnet:v1:onlexnet.pdt.market.events.MarketChangedEvent --data '{"ticker": "SAS", "whenyyyymmddhhmm": 200102030405, "date": 20010203, "open": 20, "high": 20, "low": 10, "close": 25, "adjClose": 27, "volume": 100 }'
