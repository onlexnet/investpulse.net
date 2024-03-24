# Scope
- Distribute locally in real time changes

## Purpose
On testing environment we need a centralized place to emit time changes, so that we may speedup processes as much as we need to see final results. Of course it builds some concerns
Q1: - How fast should we emit events?
Q2: - when to start emit the first event?

About Q1:
- Scheduler should emit time event and wait with the next event when all known consumer will confirm applying of side-effect operations as 'done'
About Q2:
- Scheduler should wait for all known clients before emitting first event. If not all clients are ready - should fail. If there is different number of clients than expected -  should fail

In real scenario (using real time), Schedule should not wait for listeners, just simply emit time events for interested listeners.

To distinguish test and real scenario, Scheduler has to be informed upfront about start:
NUMBER_OF_TIME_CLIENTS=x, where x is e.g. 5
- Application is waiting 10 secs for all clients
- If number of clients is not equal x, it stops working.
- If number of client will increase after start of emiting time events, application will stop working
- all applications are obligated to emit Progress event

or

NUMBER_OF_TIME_CLIENTS=REAL
what means application should emit real time. 


## run standalone
dapr run --app-protocol grpc --app-port 50000 --app-id scheduler python app.py

# Run tests
```
pytest -v
```

## used articles
- https://grpc.io/docs/languages/python/basics/#generating-client-and-server-code
- [Python grpc client and server](https://www.youtube.com/watch?v=WB37L7PjI5k)
