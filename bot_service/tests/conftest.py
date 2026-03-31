from collections.abc import AsyncGenerator

import fakeredis.aioredis
import pytest_asyncio


@pytest_asyncio.fixture
async def fake_redis() -> AsyncGenerator:
    redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield redis_client
    await redis_client.flushall()
    await redis_client.aclose()