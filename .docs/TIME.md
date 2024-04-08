# How to manage time


- uservice-scheduler emits real time every 1 minute

For testing purpose:
- uservice-scheduler starts with information, how many time clients would like to be informed about time changes
- each consumer is informed and returns:
  - information how more clients they invoted to observe the current change
  - what is the next expected time when they would like to be informed about time change
  - as the result, the scheduler has to wait for all clients baout confirmation, and emits next time change choosing the closest time required by any of clients

- when Event contains timemarker
