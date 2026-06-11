import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

_URL = "https://generativelanguage.googleapis.com/v1/models/text-embedding-004:embedContent"


def _embed_one(text: str) -> list[float]:
    response = httpx.post(
        _URL,
        params={"key": os.getenv("GOOGLE_API_KEY")},
        json={"content": {"parts": [{"text": text}]}},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()["embedding"]["values"]


def _embed_sync(texts: list[str]) -> list[list[float]]:
    return [_embed_one(t) for t in texts]


async def embed_texts(texts: list[str]) -> list[list[float]]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _embed_sync, texts)


async def embed_query(text: str) -> list[float]:
    vectors = await embed_texts([text])
    return vectors[0]
