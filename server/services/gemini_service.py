import asyncio
import json
import logging
import os
import re
import uuid
from mcp import ClientSession, StdioServerParameters as McpStdioParams
from mcp.client.stdio import stdio_client

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", os.getenv("GOOGLE_CLOUD_PROJECT", "firstaid-agent"))
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from services.plants_service import get_nearby_plants
from services.dd_plants_service import search_plants_by_activities, filter_plants_by_activities
from services.unified_ethnobotanies_service import find_plants_by_region

logger = logging.getLogger(__name__)

_UNSAFE_PLANTS = {
    # Scientific binomials
    "ricinus communis",
    "senecio jacobaea",
    "arnica montana",
    "lunaria annua",
    "jatropha curcas",
    "solanum incanum",
    "datura stramonium",
    "carica papaya",
    "plumbago zeylanica",
    # African
    "rauwolfia vomitoria",
    "voacanga africana",
    # Indian
    "euphorbia neriifolia",
    # European pharmacopoeial names (latin_name field in European DB)
    "arnicae flos",
    "arnicae herba",
    "arnicae radix",
    "senecionis herba",
    "solanum dulcamara",
    "solani dulcamarae",    # pharmacopoeial form in European DB (Solani dulcamarae stipites)
    "paeoniae radix",       # covers both Paeoniae radix rubra and Paeoniae radix alba
    "glycini semen",
    "soiae oleum",          # soybean oil preparations (Soiae oleum raffinatum, etc.)
    "balsamum peruvianum",
    "uncariae tomentosae",
    "picrorhizae kurroae",
    "visci albi",
    "chelidonii herba",
    "saccharomyces cerevisiae",
    "caryophylli flos",
    "piperis methystici",
    "allii cepae",
    "cannabis flos",
    "adhatodae vasicae",
    "angelicae sinensis",
    "withaniae somniferae",
    "sambuci fructus",
    "calendulae herba",
    "euphrasiae herba",
    "citri bergamiae",
    "salviae trilobae",
    "andrographidis paniculatae",
    "tiliae tomentosae",
    "salviae officinalis",
    "capsici fructus",          # capsaicin harmful on open wounds
    "symphyti radix",           # pyrrolizidine alkaloids, liver toxicity risk
    "salviae miltiorrhizae",    # blood-thinning properties, warfarin interactions
    # Chinese pharmacopoeial names (Herb_latin_name field in Chinese DB)
    "crotonis fructus",
    "dysosma versipellis",
    "typhonii rhizoma",
    "gleditsiae fructus",
    "schisandrae chinensis",
    "phellodendri amurensis",
    "herba hyperici",
    "herba corydalis",
    "radix smilacis",
    "peucedani decursivi",
    "gleditsiae spina",
    "mylabris",
}


def _normalize_name(name: str | None) -> str:
    """Return lowercase 'Genus species', stripping author names and variety suffixes."""
    if not name:
        return ""
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0].lower()} {parts[1].lower()}"
    return parts[0].lower() if parts else ""


def _is_unsafe(name: str | None) -> bool:
    return _normalize_name(name) in _UNSAFE_PLANTS
SAFE_USE_TYPES = [
    "Analgesic", "Dermatological Aid", "Gastrointestinal Aid",
    "Cold Remedy", "Respiratory Aid", "Throat Aid", "Hemostat",
    "Antirheumatic (External)", "Antidiarrheal", "Diuretic",
    "Laxative", "Febrifuge", "Antiemetic", "Wound Remedy"
]


EXCLUDE_USE_TYPES = [
    "Panacea", "Unspecified", "Tuberculosis Remedy",
    "Eye Medicine", "Heart Medicine", "Venereal Aid",
    "Ceremonial Medicine", "Snake Bite Remedy", "Preventive Medicine",
]

_APP_NAME = "firstaid_agent"
_MCP_DB = "MCP"
_MCP_COLLECTION = "analysis"


def _filter_unsafe(plants: list) -> list:
    return [
        p for p in plants
        if not _is_unsafe(p.get("scientificName", p.get("taxon")))
    ]


# --- ADK Tool Functions ---

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


async def search_african_ethnobotanies(keywords: list[str], relevant_categories: list[str] | None = None) -> str:
    """Search the African ethnobotany database for plants that treat a condition.

    Args:
        keywords: Therapeutic keywords e.g. ['wound', 'inflammation', 'antiseptic'].
        relevant_categories: Restrict results to these health problem categories. Available values:
            'Skin conditions', 'Wound healing', 'Burns', 'Infections', 'Pain',
            'Respiratory infections', 'Diarrhea', 'Malaria', 'Worms', 'Asthma'.
            Pass only categories relevant to the condition.
    """
    logger.info(f"[TOOL] search_african_ethnobotanies(keywords={keywords}, relevant_categories={relevant_categories})")
    results = await find_plants_by_region(keywords, "African")
    results = [r for r in results if not _is_unsafe(r.latin_name)]
    logger.info(f"[TOOL] search_african_ethnobotanies → {len(results)} results")
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
    results = await find_plants_by_region(keywords, "Chinese")
    results = [r for r in results if not _is_unsafe(r.latin_name)]
    logger.info(f"[TOOL] search_chinese_ethnobotanies → {len(results)} results")
    seen: set[str] = set()
    deduped = []
    for r in results:
        key = r.common_name or r.latin_name
        if key and key not in seen:
            seen.add(key)
            deduped.append(r)
    return json.dumps([
        {
            "common_name": r.common_name,
            "pharmacopoeial_name": r.latin_name,
            "function": r.function,
            "actions": r.tcmwiki_actions,
            "part_used": r.part_used,
            "dosage": r.tcmwiki_dosage,
            "preparation": r.preparation,
        }
        for r in deduped
    ])


async def search_indian_ethnobotanies(keywords: list[str]) -> str:
    """Search the Indian ethnobotany database for plants that treat a condition.

    Args:
        keywords: Therapeutic keywords e.g. ['wound', 'inflammation', 'skin'].
    """
    logger.info(f"[TOOL] search_indian_ethnobotanies(keywords={keywords})")
    results = await find_plants_by_region(keywords, "Indian")
    results = [r for r in results if not _is_unsafe(r.latin_name)]
    logger.info(f"[TOOL] search_indian_ethnobotanies → {len(results)} results")
    return json.dumps([
        {
            "common_name": r.common_name,
            "botanical_name": r.latin_name,
            "part_used": r.part_used,
            "therapeutic_uses": r.therapeutic_uses,
            "dosage": r.dose,
        }
        for r in results
    ])


async def search_north_american_ethnobotanies(keywords: list[str]) -> str:
    """Search the North American ethnobotany database for plants that treat a condition.
    Use this for any location in the USA, Canada, or Mexico.

    Args:
        keywords: Therapeutic keywords e.g. ['wound', 'inflammation', 'skin'].
    """
    logger.info(f"[TOOL] search_north_american_ethnobotanies(keywords={keywords})")
    results = await find_plants_by_region(
        keywords, "North American",
        safe_use_types=SAFE_USE_TYPES,
        exclude_use_types=EXCLUDE_USE_TYPES,
    )
    results = [r for r in results if not _is_unsafe(r.latin_name)]
    logger.info(f"[TOOL] search_north_american_ethnobotanies → {len(results)} results")
    return json.dumps([
        {
            "common_name": r.common_name,
            "scientific_name": r.latin_name,
            "use_type": r.use_type,
            "description": r.description,
        }
        for r in results
    ])


async def search_european_ethnobotanies(keywords: list[str], relevant_areas: list[str] | None = None) -> str:
    """Search the European ethnobotany database for plants that treat a condition.

    Args:
        keywords: Therapeutic keywords e.g. ['wound healing', 'anti-inflammatory'].
        relevant_areas: Restrict results to these therapeutic categories. Available values:
            'Skin disorders and minor wounds', 'Pain and inflammation', 'Wound healing',
            'Cough and cold', 'Gastrointestinal disorders', 'Mouth and throat disorders',
            'Circulatory disorders', 'Urinary tract and genital disorders',
            'Mental stress and mood disorders', 'Eye discomfort'.
            Pass only the categories relevant to the condition.
    """
    logger.info(f"[TOOL] search_european_ethnobotanies(keywords={keywords}, relevant_areas={relevant_areas})")
    results = await find_plants_by_region(keywords, "European")
    results = [r for r in results if not _is_unsafe(r.latin_name)]
    logger.info(f"[TOOL] search_european_ethnobotanies → {len(results)} results")
    return json.dumps([
        {
            "common_name": r.common_name,
            "latin_name": r.latin_name,
            "therapeutic_area": r.therapeutic_area,
        }
        for r in results
    ])


async def search_dukes_db(keywords: list[str]) -> str:
    """Search Duke's phytochemical database for plants that treat a condition.

    Args:
        keywords: Therapeutic keywords e.g. ['vulnerary', 'antiseptic', 'wound healing'].
    """
    logger.info(f"[TOOL] search_dukes_db(keywords={keywords})")
    plants = await search_plants_by_activities(keywords=keywords)
    logger.info(f"[TOOL] search_dukes_db → {len(plants)} results")
    return json.dumps(_filter_unsafe(plants))


async def check_inat_plants_in_dukes_db(plant_names: list[str], keywords: list[str]) -> str:
    """Check which iNaturalist plants also appear in Duke's DB with relevant therapeutic activities.
    Use this to cross-reference the iNaturalist plant list against Duke's DB.

    Args:
        plant_names: Scientific names from iNaturalist e.g. ['Achillea millefolium', 'Calendula officinalis'].
        keywords: Therapeutic keywords e.g. ['wound', 'antiseptic', 'anti-inflammatory'].
    """
    logger.info(f"[TOOL] check_inat_plants_in_dukes_db(plants={plant_names}, keywords={keywords})")
    plants = await filter_plants_by_activities(plant_names=plant_names, keywords=keywords)
    logger.info(f"[TOOL] check_inat_plants_in_dukes_db → {len(plants)} matches")
    return json.dumps(_filter_unsafe(plants))



# --- Agent & Runner ---

_SYSTEM_PROMPT = (
    "You are a first aid assistant specializing in natural plant-based remedies. "
    "Follow these steps IN ORDER — do not skip ahead or call tools out of sequence:\n\n"
    "STEP 1: Identify the condition from the image and symptoms. "
    "Determine therapeutic keywords (e.g. 'inflammation', 'wound', 'antiseptic').\n\n"
    "STEP 2: Call these tools in parallel:\n"
    "   - get_nearby_plants_tool(country)\n"
    "   - Regional ethnobotany tool based on country:\n"
    "       Africa → search_african_ethnobotanies(keywords)\n"
    "       China → search_chinese_ethnobotanies(keywords)\n"
    "       Europe → search_european_ethnobotanies(keywords)\n"
    "       India → search_indian_ethnobotanies(keywords)\n"
    "       USA, Canada, Mexico, or any North American state/province → search_north_american_ethnobotanies(keywords)\n\n"
    "STEP 3: Build the remedy list:\n"
    "   - Every plant returned by the regional ethnobotany DB is a confirmed remedy — "
    "include it with source='Ethnobotany'.\n"
    "   - Take the scientificName list from get_nearby_plants_tool and call "
    "check_inat_plants_in_dukes_db(plant_names, keywords). "
    "Every plant returned is confirmed — include it with source='iNaturalist+DukesDB'.\n\n"
    "STEP 4: Return a final JSON response with exactly these keys:\n"
    '   - "condition": string describing the identified condition\n'
    '   - "country": string — the user\'s country as provided\n'
    '   - "compoundKeywords": array of therapeutic keywords used\n'
    '   - "remedyPlants": array of confirmed remedy plants, each with:\n'
    '       "commonName" (string), "pharmacopoeialName" (string — use the pharmacopoeial_name or latin_name from the DB),\n'
    '       "matchingUses" (array of strings from the DB therapeutic fields),\n'
    '       "source" (string — exactly "Ethnobotany" or "iNaturalist+DukesDB")\n'
    "Do not use your own knowledge to add plants. "
    "Return only valid JSON, no markdown or extra text."
)

_session_service = InMemorySessionService()


def _mcp_server_params():
    return McpStdioParams(
        command="npx",
        args=["-y", "mongodb-mcp-server"],
        env={**os.environ, "MDB_MCP_CONNECTION_STRING": os.getenv("MONGO_URI")},
    )


async def analyze_ailment(image_bytes: bytes, symptoms: str, country: str, user_id: str) -> dict:
    result_future: asyncio.Future[dict] = asyncio.get_running_loop().create_future()

    async def _run_with_mcp() -> None:
        try:
            async with stdio_client(_mcp_server_params()) as (read, write):
                async with ClientSession(read, write) as mcp:
                    await mcp.initialize()
                    logger.info("MCP: session started")

                    # Step 0: fetch past analyses for this user
                    history_text = ""
                    try:
                        res = await asyncio.wait_for(
                            mcp.call_tool("find", {
                                "database": _MCP_DB,
                                "collection": _MCP_COLLECTION,
                                "filter": {"user_id": user_id},
                                "limit": 3,
                            }),
                            timeout=10.0,
                        )
                        history = json.loads(res.content[0].text) if res.content else []
                        if history:
                            history_text = (
                                f"\nThis user's past analysis (use as context, avoid repeating the same plants):\n"
                                f"{json.dumps(history, indent=2)}\n"
                            )
                            logger.info(f"MCP: found {len(history)} past analysis for user")
                        else:
                            logger.info("MCP: no past analysis found for user")
                    except Exception as e:
                        logger.warning(f"MCP find failed (non-fatal): {e}")

                    agent = LlmAgent(
                        name=_APP_NAME,
                        model="gemini-2.5-flash",
                        instruction=_SYSTEM_PROMPT,
                        tools=[
                            get_nearby_plants_tool,
                            search_african_ethnobotanies,
                            search_chinese_ethnobotanies,
                            search_european_ethnobotanies,
                            search_indian_ethnobotanies,
                            search_north_american_ethnobotanies,
                            check_inat_plants_in_dukes_db,
                        ],
                    )

                    runner = Runner(agent=agent, app_name=_APP_NAME, session_service=_session_service)
                    session = await _session_service.create_session(
                        app_name=_APP_NAME,
                        user_id=user_id,
                        session_id=str(uuid.uuid4()),
                    )

                    message = types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                            types.Part(
                                text=(
                                    f"Symptoms: {symptoms}\n"
                                    f"User country: {country}\n"
                                    f"{history_text}\n"
                                    "Follow the steps in the system prompt exactly."
                                )
                            ),
                        ],
                    )

                    final_text = None
                    async for event in runner.run_async(
                        user_id=user_id,
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
                    result = json.loads(final_text)

                    # Resolve the future BEFORE context managers exit so the HTTP
                    # response is sent even if MCP cleanup hangs.
                    result_future.set_result(result)

                    asyncio.create_task(_mcp_save(user_id, symptoms, country, result))
                    # Context managers exit here; cleanup may be slow but no longer blocks the caller.

        except Exception as e:
            if not result_future.done():
                result_future.set_exception(e)

    asyncio.create_task(_run_with_mcp())
    return await result_future


async def _mcp_save(user_id: str, symptoms: str, country: str, result: dict) -> None:
    try:
        async with stdio_client(_mcp_server_params()) as (read, write):
            async with ClientSession(read, write) as mcp:
                await mcp.initialize()
                save_res = await asyncio.wait_for(
                    mcp.call_tool("insert-many", {
                        "database": _MCP_DB,
                        "collection": _MCP_COLLECTION,
                        "documents": [{
                            "user_id": user_id,
                            "symptoms": symptoms,
                            "country": country,
                            "condition": result.get("condition"),
                            "compoundKeywords": result.get("compoundKeywords", []),
                            "remedyPlants": result.get("remedyPlants", []),
                        }],
                    }),
                    timeout=10.0,
                )
                save_text = save_res.content[0].text if save_res.content else ""
                if '"error"' in save_text.lower() or '"iserror": true' in save_text.lower():
                    logger.warning(f"MCP save returned error: {save_text}")
                else:
                    logger.info(f"MCP: analysis saved to 'analysis' collection: {save_text}")
    except BaseException as e:
        logger.warning(f"MCP save failed (non-fatal): {e}")
