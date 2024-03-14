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
