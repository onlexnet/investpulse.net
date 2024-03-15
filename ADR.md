# ADR

## ADR 1
Context: We are going to share aplication events across uservices

Decision: Use AVRO for serialization

Reasons:
- Already used in messaging like Kafka
- good tooling set to generate classes for java and python

Alternatives:
- protobuf (schema separated from message)
- json (schemaless)

Consequences:
- new tools to learn

## ADR 2
Context: Events serialization

Decision: use events as pure JSON messages, ignoring schema

Reasons:
- I can't find simple way of how to serialize binary messages and deserialize them
- when serialized to binaries, DAPR seems to save binary content as string in REDIS
- ignoring schema and using just JSON representation looks very simple from coding perspective

Alternatives:
- get more knowledge about serialization options related to AVBRO and DAPR pubsub
