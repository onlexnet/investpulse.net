import json
from typing import Any
from dapr.clients import DaprClient

def publish(dc: DaprClient, event: Any):

  schema_prefix = "onlexnet:v1"
  topic_name = f"{schema_prefix}:{event.RECORD_SCHEMA.fullname}"

  event_as_dict = event.to_avro_writable()
  as_json = json.dumps(event_as_dict)
  dc.publish_event(pubsub_name="pubsub", topic_name=topic_name, data = as_json, data_content_type="application/json", publish_metadata={ "ttlInSeconds": "10" })

