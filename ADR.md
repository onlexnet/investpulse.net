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
Context: Topic convention in pubsub scenarios

Decision: single topic per single message

Reasons:
- Topic naming per conventions saves code and make such assymption very easy to explain
- Already proven as workign solution in another project

Alternatives:
- recognize message type by extra metadata in cloudevent metadata
