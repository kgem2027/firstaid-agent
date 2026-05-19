import httpx


async def get_nearby_plants(latitude: float, longitude: float) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.inaturalist.org/v1/observations",
            params={
                "lat": latitude,
                "lng": longitude,
                "radius": 50,
                "taxon_name": "Plantae",
                "quality_grade": "research",
                "per_page": 20,
                "order_by": "observed_on",
            },
        )
        data = response.json()

    results = data.get("results", [])
    if not results:
        raise ValueError("No plants found in this area")

    plants = [
        {
            "id": obs["taxon"]["id"],
            "scientificName": obs["taxon"]["name"],
            "commonName": obs["taxon"].get("preferred_common_name") or obs["taxon"]["name"],
            "iconicTaxon": obs["taxon"].get("iconic_taxon_name"),
        }
        for obs in results
        if obs.get("taxon")
    ]

    # Remove duplicates by scientific name
    seen = set()
    unique_plants = []
    for p in plants:
        if p["scientificName"] not in seen:
            seen.add(p["scientificName"])
            unique_plants.append(p)

    return unique_plants
