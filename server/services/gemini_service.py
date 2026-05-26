import json
import logging
import os
import re

from google import genai
from google.genai import types

from services.plants_service import get_nearby_plants
from services.dd_plants_service import search_plants_by_activities

logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_UNSAFE_PLANTS = {
    "Ricinus communis",      # ricin toxicity
    "Senecio jacobaea",      # pyrrolizidine alkaloids
    "Arnica montana",        # not for open wounds
    "Lunaria annua",
}


def _filter_unsafe(plants: list) -> list:
    return [
        p for p in plants
        if p.get("scientificName", p.get("taxon", "")) not in _UNSAFE_PLANTS
    ]


_SYSTEM_PROMPT = (
    "You are a first aid assistant specializing in natural plant-based remedies. "
    "Given an image of a wound or condition and the user's symptoms, your job is to:\n"
    "1. Identify the condition from the image and symptoms.\n"
    "2. Determine the therapeutic keywords for this condition (e.g. 'vulnerary', 'antiseptic', 'wound healing').\n"
    "3. Call BOTH tools in parallel:\n"
    "   - get_nearby_plants(country) — returns locally observed plants from iNaturalist.\n"
    "   - search_dukes_db(keywords) — returns plants from Duke's phytochemical database.\n"
    "4. From get_nearby_plants results: these are the PRIMARY source. Include EVERY plant from this list "
    "that has any known or plausible medicinal use related to the condition — be very inclusive. "
    "Only exclude a plant if it is definitively and well-known to be toxic to humans with zero medicinal use. "
    "Do NOT exclude plants just because they are uncommon — if there is any traditional or documented use "
    "for this condition, include it. Populate matchingUses from your knowledge for each plant.\n"
    "5. From search_dukes_db results: add any plants NOT already included from iNaturalist as secondary results.\n"
    "6. Return a final JSON response with exactly these keys:\n"
    '   - "condition": string describing the identified condition\n'
    '   - "compoundKeywords": array of therapeutic property strings used in the search\n'
    '   - "remedyPlants": array of ALL remedy plants, iNaturalist plants listed first, each with:\n'
    '       "commonName" (string), "scientificName" (string),\n'
    '       "matchingUses" (array of strings),\n'
    '       "source" (string — exactly "iNaturalist" or "DukesDB")\n'
    "Return only valid JSON, no markdown or extra text."
)

_TOOLS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_nearby_plants",
            description=(
                "Find plants observed in a country via iNaturalist. "
                "Returns a list of locally observed plant species."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "country": types.Schema(
                        type=types.Type.STRING,
                        description="The country or region name, e.g. 'China' or 'California'",
                    ),
                },
                required=["country"],
            ),
        ),
        types.FunctionDeclaration(
            name="search_dukes_db",
            description=(
                "Search Duke's phytochemical and ethnobotanical database for plants with specific "
                "therapeutic activities. Returns plants whose documented uses match the keywords."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "keywords": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                        description=(
                            "Therapeutic activity keywords to search for, "
                            "e.g. ['vulnerary', 'wound healing', 'antiseptic', 'anti-inflammatory']"
                        ),
                    ),
                },
                required=["keywords"],
            ),
        ),
    ]
)


async def _run_tool(name: str, args: dict) -> str:
    logger.info(f"Gemini tool call: {name}({args})")
    if name == "get_nearby_plants":
        try:
            plants = await get_nearby_plants(**args)
            return json.dumps(_filter_unsafe(plants))
        except ValueError as e:
            return json.dumps({"error": str(e), "plants": []})
    if name == "search_dukes_db":
        plants = await search_plants_by_activities(**args)
        return json.dumps(_filter_unsafe(plants))
    return json.dumps({"error": f"Unknown tool: {name}"})


async def analyze_ailment(
    image_bytes: bytes, symptoms: str, country: str
) -> dict:
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                types.Part(
                    text=(
                        f"Symptoms: {symptoms}\n"
                        f"User country: {country}\n\n"
                        f"Call get_nearby_plants with country=\"{country}\" AND search_dukes_db with "
                        "relevant keywords at the same time. List iNaturalist plants first, then any "
                        "additional plants from Duke's DB. Return your final answer as JSON."
                    )
                ),
            ],
        )
    ]

    for _ in range(10):
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                tools=[_TOOLS],
            ),
        )

        candidate = response.candidates[0]
        function_calls = [p for p in candidate.content.parts if p.function_call is not None]

        if not function_calls:
            text = response.text.strip()
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            return json.loads(text)

        contents.append(types.Content(role="model", parts=candidate.content.parts))

        tool_result_parts = []
        for part in function_calls:
            fc = part.function_call
            result = await _run_tool(fc.name, dict(fc.args))
            tool_result_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=fc.name,
                        response={"result": result},
                    )
                )
            )
        contents.append(types.Content(role="user", parts=tool_result_parts))

    raise RuntimeError("Gemini agentic loop exceeded maximum rounds without a final response")
