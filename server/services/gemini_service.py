import json
import logging
import os
import re
import uuid

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", os.getenv("GOOGLE_CLOUD_PROJECT", "firstaid-agent"))
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from google.genai import types

from services.plants_service import get_nearby_plants
from services.dd_plants_service import search_plants_by_activities
from services.african_ethnobotanies_service import find_plants_by_condition as find_african
from services.chinese_ethnobotanies_service import find_plants_by_condition as find_chinese
from services.european_ethnobotanies_service import find_plants_by_condition as find_european

logger = logging.getLogger(__name__)

_UNSAFE_PLANTS = {
    "Ricinus communis",
    "Senecio jacobaea",
    "Arnica montana",
    "Lunaria annua",
}

_APP_NAME = "firstaid_agent"


def _filter_unsafe(plants: list) -> list:
    return [
        p for p in plants
        if p.get("scientificName", p.get("taxon", "")) not in _UNSAFE_PLANTS
    ]


# --- ADK Tool Functions ---
# ADK reads the function signature + docstring to generate the tool schema.

async def get_nearby_plants_tool(country: str) -> str:
    """Find plants observed in a country via iNaturalist. Returns a JSON list of locally observed plant species.

    Args:
        country: The country or region name, e.g. 'China' or 'California'.
    """
    logger.info(f"[TOOL] get_nearby_plants(country={country})")
    try:
        plants = await get_nearby_plants(country=country)
        return json.dumps(_filter_unsafe(plants))
    except ValueError as e:
        return json.dumps({"error": str(e), "plants": []})


async def search_african_ethnobotanies(keywords: list[str]) -> str:
    """Search the African ethnobotany database for plants that treat a condition.

    Args:
        keywords: Therapeutic keywords e.g. ['wound', 'inflammation', 'antiseptic'].
    """
    logger.info(f"[TOOL] search_african_ethnobotanies(keywords={keywords})")
    results = await find_african(keywords=keywords)
    return json.dumps([
        {"latin_name": r.latin_name, "health_problems": r.health_problems, "description": r.description}
        for r in results
    ])


async def search_chinese_ethnobotanies(keywords: list[str]) -> str:
    """Search the Chinese ethnobotany database for plants that treat a condition.

    Args:
        keywords: Therapeutic keywords e.g. ['inflammation', 'skin', 'detoxify'].
    """
    logger.info(f"[TOOL] search_chinese_ethnobotanies(keywords={keywords})")
    results = await find_chinese(keywords=keywords)
    return json.dumps([
        {"latin_name": r.Herb_latin_name, "function": r.Function, "actions": r.tcmwiki_actions}
        for r in results
    ])


async def search_european_ethnobotanies(keywords: list[str]) -> str:
    """Search the European ethnobotany database for plants that treat a condition.

    Args:
        keywords: Therapeutic keywords e.g. ['wound healing', 'anti-inflammatory'].
    """
    logger.info(f"[TOOL] search_european_ethnobotanies(keywords={keywords})")
    results = await find_european(keywords=keywords)
    return json.dumps([
        {"latin_name": r.latin_name, "therapeutic_area": r.therapeutic_area}
        for r in results
    ])


async def search_dukes_db(keywords: list[str]) -> str:
    """Search Duke's phytochemical database for plants that treat a condition.

    Args:
        keywords: Therapeutic keywords e.g. ['vulnerary', 'antiseptic', 'wound healing'].
    """
    logger.info(f"[TOOL] search_dukes_db(keywords={keywords})")
    plants = await search_plants_by_activities(keywords=keywords)
    return json.dumps(_filter_unsafe(plants))


# --- Agent & Runner ---

_SYSTEM_PROMPT = (
    "You are a first aid assistant specializing in natural plant-based remedies. "
    "Follow these steps IN ORDER — do not skip ahead or call tools out of sequence:\n\n"
    "STEP 1: Identify the condition from the image and symptoms. "
    "Determine therapeutic keywords (e.g. 'inflammation', 'wound', 'antiseptic').\n\n"
    "STEP 2: Call get_nearby_plants_tool(country) AND the appropriate regional ethnobotany tool in parallel:\n"
    "   - Africa → search_african_ethnobotanies(keywords)\n"
    "   - China → search_chinese_ethnobotanies(keywords)\n"
    "   - Europe → search_european_ethnobotanies(keywords)\n"
    "   - Any region → search_dukes_db(keywords) as an additional source\n\n"
    "STEP 3: Build the remedy list:\n"
    "   - Every plant returned by the regional ethnobotany DB is a confirmed remedy — "
    "include it with source='Ethnobotany'. No iNaturalist cross-reference needed.\n"
    "   - For iNaturalist plants NOT found in the ethnobotany DB, check the DukesDB results. "
    "If a plant appears in both iNaturalist AND DukesDB, include it with source='iNaturalist+DukesDB'.\n\n"
    "STEP 4: Return a final JSON response with exactly these keys:\n"
    '   - "condition": string describing the identified condition\n'
    '   - "compoundKeywords": array of therapeutic keywords used\n'
    '   - "remedyPlants": array of confirmed remedy plants, each with:\n'
    '       "commonName" (string), "scientificName" (string),\n'
    '       "matchingUses" (array of strings from the DB therapeutic fields),\n'
    '       "source" (string — exactly "Ethnobotany" or "iNaturalist+DukesDB")\n'
    "Do not use your own knowledge to add plants. "
    "Return only valid JSON, no markdown or extra text."
)

_DATASTORE_ID = "projects/firstaid-agent/locations/global/collections/default_collection/dataStores/ethnobotanies-datastore-v2"

_agent = LlmAgent(
    name=_APP_NAME,
    model="gemini-2.0-flash",
    instruction=_SYSTEM_PROMPT,
    tools=[
        get_nearby_plants_tool,
        search_african_ethnobotanies,
        search_chinese_ethnobotanies,
        search_european_ethnobotanies,
        search_dukes_db,
        VertexAiSearchTool(data_store_id=_DATASTORE_ID),
    ],
)

_session_service = InMemorySessionService()
_runner = Runner(agent=_agent, app_name=_APP_NAME, session_service=_session_service)


async def analyze_ailment(image_bytes: bytes, symptoms: str, country: str) -> dict:
    session = await _session_service.create_session(
        app_name=_APP_NAME,
        user_id="user",
        session_id=str(uuid.uuid4()),
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            types.Part(
                text=(
                    f"Symptoms: {symptoms}\n"
                    f"User country: {country}\n\n"
                    "Follow the steps in the system prompt exactly. "
                    "Start by calling get_nearby_plants_tool, then look up each plant in the ethnobotany "
                    "and Duke's databases before returning your final JSON."
                )
            ),
        ],
    )

    final_text = None
    async for event in _runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text

    if not final_text:
        raise RuntimeError("ADK agent did not produce a final response")

    final_text = final_text.strip()
    final_text = re.sub(r"^```(?:json)?\s*", "", final_text)
    final_text = re.sub(r"\s*```$", "", final_text)
    return json.loads(final_text)
