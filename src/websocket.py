import asyncio
import dataclasses
import json
import logging
from typing import Dict

import redis.asyncio as redis
from redis.asyncio.client import PubSub
from fastapi import WebSocket


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Room:
    pubsub: PubSub
    receiver: asyncio.Task
    connections: Dict[int, WebSocket]


class WSManager:
    def __init__(self, redis: redis.Redis):
        self.rooms: Dict[str, Room] = {}
        self._redis = redis

    async def add_to_room(self, id_: str, websocket: WebSocket):
        await websocket.accept()

        if id_ in self.rooms:
            logger.info('Adding a new connection to the new room (%s)', id_)
            self.rooms[id_].connections[id(websocket)] = websocket
        else:
            logger.info('Adding a new connection to the existing room (%s)', id_)
            pubsub = self._redis.pubsub(ignore_subscribe_messages=True)
            await pubsub.subscribe(id_)

            self.rooms[id_] = Room(
                pubsub=pubsub,
                receiver=asyncio.create_task(self.receiver(pubsub)),
                connections={id(websocket): websocket},
            )

    async def remove_from_room(self, id_: str, websocket: WebSocket):
        if id_ in self.rooms:
            logger.info('Removing a connection from the room (%s)', id_)
            participants = self.rooms[id_]
            participants.connections.pop(id(websocket), None)

            if len(participants.connections) == 0:
                logger.info('The room (%s) is empty, removing room and unsubscribe from the channel.', id_)
                self.rooms.pop(id_)
                await participants.pubsub.unsubscribe(id_)
                participants.receiver.cancel()

    async def receiver(self, pubsub: PubSub):
        while True:
            message = await pubsub.get_message()

            if message:
                logger.info('Message received: %s', json.dumps(message))
                room_id = message['channel']
                participants = self.rooms.get(room_id)

                if participants:
                    for websocket in participants.connections.values():
                        await websocket.send_text(message['data'])
