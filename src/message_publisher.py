import asyncio
import random

import redis.asyncio as redis

from config import settings


async def amain():
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )

    room_pool = list(map(str, range(0, 10)))

    while True:
        room_id = random.choice(room_pool)

        await redis_client.publish(
            channel=room_id,
            message=f'message for {room_id} room'
        )
        await asyncio.sleep(1)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(amain())


if __name__ == '__main__':
    main()
