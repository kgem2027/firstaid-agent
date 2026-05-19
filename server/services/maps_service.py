import httpx
import os


async def get_location_name(latitude: float, longitude: float) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"latlng": f"{latitude},{longitude}", "key": os.getenv("GOOGLE_MAPS_API_KEY")},
        )
        data = response.json()

    results = data.get("results", [])
    if not results:
        raise ValueError("No location found for these coordinates")

    return {
        "latitude": latitude,
        "longitude": longitude,
        "placeName": results[0]["formatted_address"],
    }
