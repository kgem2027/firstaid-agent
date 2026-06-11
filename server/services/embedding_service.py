import asyncio
import logging
import os

from google import genai

logger = logging.getLogger(__name__)

_MODEL = "text-embedding-004"


def _get_client() -> genai.Client:
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    if project:
        # In GCP deployment, use Vertex AI backend with service account ADC
        return genai.Client(vertexai=True, project=project, location=location)
    # Local dev: use Gemini API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    return genai.Client(api_key=api_key)


def _embed_one(text: str) -> list[float]:
    client = _get_client()
    response = client.models.embed_content(model=_MODEL, contents=text)
    return response.embeddings[0].values


def _embed_sync(texts: list[str]) -> list[list[float]]:
    return [_embed_one(t) for t in texts]


async def embed_texts(texts: list[str]) -> list[list[float]]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _embed_sync, texts)


async def embed_query(text: str) -> list[float]:
    vectors = await embed_texts([text])
    return vectors[0]
