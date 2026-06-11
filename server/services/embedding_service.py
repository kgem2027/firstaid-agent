import asyncio
import logging
import os

from google import genai

logger = logging.getLogger(__name__)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    return _client


def _embed_sync(texts: list[str]) -> list[list[float]]:
    client = _get_client()
    results = []
    for text in texts:
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=text,
        )
        results.append(result.embeddings[0].values)
    return results


async def embed_texts(texts: list[str]) -> list[list[float]]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _embed_sync, texts)


async def embed_query(text: str) -> list[float]:
    vectors = await embed_texts([text])
    return vectors[0]
