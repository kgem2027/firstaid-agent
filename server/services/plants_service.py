import httpx


# Known medicinal plant family taxon IDs on iNaturalist
MEDICINAL_TAXON_IDS = [
    47219,  # Asteraceae (Calendula, Yarrow, Chamomile)
    47603,  # Lamiaceae (Mint, Sage, Self-heal, Thyme)
    47724,  # Rosaceae (Agrimony, Burnet)
    47725,  # Plantaginaceae (Plantain)
    48626,  # Hypericaceae (St. John's Wort)
    47727,  # Apiaceae
]

async def get_nearby_plants(country: str) -> list:
    async with httpx.AsyncClient() as client:
        place_resp = await client.get(
            "https://api.inaturalist.org/v1/places/autocomplete",
            params={"q": country, "per_page": 1},
        )
        place_data = place_resp.json()
        results_places = place_data.get("results", [])
        if not results_places:
            raise ValueError(f"Could not find iNaturalist place for country: {country}")
        place_id = results_places[0]["id"]

        all_plants = []
        seen = set()

        for taxon_id in MEDICINAL_TAXON_IDS:
            response = await client.get(
                "https://api.inaturalist.org/v1/observations",
                params={
                    "place_id": place_id,
                    "taxon_id": taxon_id,
                    "quality_grade": "research",
                    "captive": "false",
                    "per_page": 20,
                    "order_by": "observations_count",
                },
            )
            data = response.json()
            for obs in data.get("results", []):
                if not obs.get("taxon"):
                    continue
                taxon = obs["taxon"]
                name = taxon["name"]
                # Skip anything above species level
                if taxon.get("rank") not in ("species", "subspecies"):
                    continue
                if name not in seen:
                    seen.add(name)
                    all_plants.append({
                        "id": taxon["id"],
                        "scientificName": name,
                        "commonName": taxon.get("preferred_common_name") or name,
                        "iconicTaxon": taxon.get("iconic_taxon_name"),
                    })

        return all_plants