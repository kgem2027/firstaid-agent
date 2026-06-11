import asyncio
import logging
import os
import tempfile

from google import genai

logger = logging.getLogger(__name__)

_MODEL = "text-embedding-004"
_tmp_creds_path: str | None = None


def _ensure_adc() -> None:
    """If GOOGLE_APPLICATION_CREDENTIALS_JSON is set, write it to a temp file
    so that ADC can find it. Only runs once per process."""
    global _tmp_creds_path
    if _tmp_creds_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        return
    creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not creds_json:
        return
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(creds_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
        _tmp_creds_path = path
        logger.info("embedding_service: wrote ADC credentials from env var")
    except Exception as e:
        logger.warning(f"embedding_service: could not write ADC credentials: {e}")


def _get_client() -> genai.Client:
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    if project:
        _ensure_adc()
        return genai.Client(vertexai=True, project=project, location=location)
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
