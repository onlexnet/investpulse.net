"""
I can't find DAPR callback contract models defined here
https://github.com/dapr/dapr/blob/master/dapr/proto/runtime/v1/appcallback.proto

So atm I need my own equivalents serialized to DAPR target messages

"""


from dataclasses import dataclass


# // TopicSubscription represents topic and metadata.
# message TopicSubscription {
#   // Required. The name of the pubsub containing the topic below to subscribe to.
#   string pubsub_name = 1;

#   // Required. The name of topic which will be subscribed
#   string topic = 2;

#   // The optional properties used for this topic's subscription e.g. session id
#   map<string,string> metadata = 3;

#   // The optional routing rules to match against. In the gRPC interface, OnTopicEvent
#   // is still invoked but the matching path is sent in the TopicEventRequest.
#   TopicRoutes routes = 5;

#   // The optional dead letter queue for this topic to send events to.
#   string dead_letter_topic = 6;

#   // The optional bulk subscribe settings for this topic.
#   BulkSubscribeConfig bulk_subscribe = 7;
# }
@dataclass
class TopicSubscription:
  # Required. The name of the pubsub containing the topic below to subscribe to.
  pubsub_name: str

  # Required. The name of topic which will be subscribed
  topic: str


# // ListTopicSubscriptionsResponse is the message including the list of the subscribing topics.
# message ListTopicSubscriptionsResponse {
#   // The list of topics.
#   repeated TopicSubscription subscriptions = 1;
# }
@dataclass
class ListTopicSubscriptionsResponse:
  # The list of topics.
  subscriptions: list[TopicSubscription]


