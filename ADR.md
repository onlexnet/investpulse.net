# ADR

## ADR 1
Context: We are going to share aplication events across uservices

Decision: Use AVRO for serialization

Reasons:
- Already used in messaging like Kafka, with forced schema verification
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

## ADR 3
Context: Topic convention in pubsub scenarios

Decision: single topic per single message

Reasons:
- Topic naming per conventions saves code and make such assymption very easy to explain
- Already proven as workign solution in another project

Alternatives:
- recognize message type by extra metadata in cloudevent metadata

## ADR 4
Context: Time management

Decision: Create single service 'uservice-scheduler' to emit time changes

Reasons:
- For testing purposes we need to have ability to run 'whole' system and see side effects of operations on much faster event loop that realtime as we have operations 

Alternatives:
- I do not see altertatives TBH


