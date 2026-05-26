from services.gemini_service import analyze_ailment


async def find_remedies(
    image_bytes: bytes, symptoms: str, country: str 
) -> dict:
    return await analyze_ailment(image_bytes, symptoms, country)
