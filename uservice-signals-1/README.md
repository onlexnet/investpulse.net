# Scope
Service designed to create SELL/BUY signals

# Details
It uses [Technical Analysis Library in Python](https://pypi.org/project/ta/)
ta==0.11.0

## Run
dapr run --app-protocol grpc --app-port 50054 --app-id scheduler --resources-path ../.components python app.py
