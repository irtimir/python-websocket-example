# Python websockets example

## Get started

```shell
docker compose up
```

## How it works

### Server

Accepts websocket connections and keeps them in a global state.

Through Redis Pub/Sub, multiple servers and the rest of the system communicate to send a message. 
Redis Pub/Sub is needed to avoid the O(N) problem: if you need to send a message, 
each of the servers subscribes to Redis channels of those clients with which it has a connection.

### Message publisher

Once a second it generates a message simulating messages from an external message source, 
selecting a channel randomly from 0 to 9.

### How to check

Start the system in docker compose and try to connect to reading messages from channel 0-9.

Example:

```shell
websocat ws://localhost:8000/ws/1
websocat ws://localhost:8000/ws/2
websocat ws://localhost:8000/ws/6
websocat ws://localhost:8000/ws/9
```

You can connect to the same channel simultaneously from different terminals, 
and then you will receive the same messages in different clients.