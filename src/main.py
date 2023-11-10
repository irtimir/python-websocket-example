import logging.config
import redis.asyncio as redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from websocket import WSManager
from config import settings, log_settings

logging.config.dictConfig(log_settings.dict())

app = FastAPI()

ws_manager = WSManager(redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
))


@app.websocket('/ws/{user_uuid}')
async def ws(websocket: WebSocket, user_uuid: str):
    await ws_manager.add_to_room(user_uuid, websocket)

    try:
        while True:
            await websocket.receive()
    except (WebSocketDisconnect, RuntimeError):
        await ws_manager.remove_from_room(user_uuid, websocket)
