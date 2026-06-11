import asyncio
import logging
import os

import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

logger = logging.getLogger(__name__)

_model: TextEmbeddingModel | None = None


def _get_model() -> TextEmbeddingModel:
    global _model
    if _model is None:
        vertexai.init(
            project=os.getenv("GOOGLE_CLOUD_PROJECT", "firstaid-agent"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
        _model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    return _model


def _embed_sync(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    inputs = [TextEmbeddingInput(t, "SEMANTIC_SIMILARITY") for t in texts]
    return [r.values for r in model.get_embeddings(inputs)]


async def embed_texts(texts: list[str]) -> list[list[float]]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _embed_sync, texts)


async def embed_query(text: str) -> list[float]:
    vectors = await embed_texts([text])
    return vectors[0]
