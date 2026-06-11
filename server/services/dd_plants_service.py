import asyncio
import logging
import re
from models.dd_plants import DDPlant
from models.farmacies import Farmacy
from models.ethnobotanies import Ethnobotany
from models.chemicals import Chemical

logger = logging.getLogger(__name__)


def _normalize_taxon(taxon: str) -> str:
    # Duke's DB stores "Genus species" only — strip variety, subspecies, and author names
    taxon = taxon.split(" var. ")[0].split(" subsp. ")[0].split(" ssp. ")[0]
    parts = taxon.split()
    # Keep only the first two parts (Genus + species), capitalize correctly
    if len(parts) >= 2:
        return f"{parts[0].capitalize()} {parts[1].lower()}"
    return taxon.strip()


async def find_plant_chemicals(taxon: str) -> dict | None:
    taxon = _normalize_taxon(taxon)
    plant, chemicals, ethnobotany = await asyncio.gather(
        DDPlant.find_one(DDPlant.taxon == taxon),
        Farmacy.find(Farmacy.taxon == taxon).to_list(),
        Ethnobotany.find(Ethnobotany.taxon == taxon).to_list(),
    )

    if not plant:
        logger.warning(f"No plant found for taxon: {taxon}")
        return None

    chem_ids = list({f.chem_id for f in chemicals if f.chem_id})
    chemical_details = await Chemical.find({"chemId": {"$in": chem_ids}}).to_list()

    logger.debug(f"Plant chemicals fetched: taxon={taxon}, farmacies={len(chemicals)}, chemicals={len(chemical_details)}")
    return {"plant": plant, "chemicals": chemicals, "chemical_details": chemical_details, "ethnobotany": ethnobotany}

async def find_plant_by_location(country: str) -> list[Ethnobotany]:
    plants = await Ethnobotany.find(Ethnobotany.country == country).to_list()
    logger.debug(f"Plants found for country '{country}': {len(plants)}")
    return plants

async def filter_plants_by_activities(plant_names: list[str], keywords: list[str]) -> list[dict]:
    """Return only plants from plant_names that have matching activities in DukesDB."""
    activity_regex = "|".join(keywords)
    normalized_lookup = {_normalize_taxon(n).lower() for n in plant_names}
    logger.info(f"filter_plants_by_activities: checking {len(normalized_lookup)} plants against DukesDB")

    records = await Ethnobotany.find(
        {"activity": {"$regex": activity_regex, "$options": "i"}}
    ).to_list()

    by_taxon: dict[str, set] = {}
    for r in records:
        if not r.taxon:
            continue
        if _normalize_taxon(r.taxon).lower() not in normalized_lookup:
            continue
        by_taxon.setdefault(r.taxon, set())
        if r.activity:
            by_taxon[r.taxon].add(r.activity)

    plants = await DDPlant.find({"taxon": {"$in": list(by_taxon.keys())}}).to_list()
    common_names = {p.taxon: p.common_names[0] if p.common_names else p.taxon for p in plants if p.taxon}

    return [
        {
            "taxon": taxon,
            "commonName": common_names.get(taxon, taxon),
            "matchingUses": list(uses),
        }
        for taxon, uses in by_taxon.items()
    ]


async def search_plants_by_activities(keywords: list[str]) -> list[dict]:
    regex = "|".join(keywords)
    records = await Ethnobotany.find(
        {"activity": {"$regex": regex, "$options": "i"}}
    ).to_list()

    by_taxon: dict[str, set] = {}
    for r in records:
        if not r.taxon:
            continue
        by_taxon.setdefault(r.taxon, set())
        if r.activity:
            by_taxon[r.taxon].add(r.activity)

    taxons = list(by_taxon.keys())
    plants = await DDPlant.find({"taxon": {"$in": taxons}}).to_list()
    common_names = {p.taxon: p.common_names[0] if p.common_names else p.taxon for p in plants if p.taxon}

    logger.debug(f"Duke's DB search for {keywords}: {len(by_taxon)} plants found")
    return [
        {
            "taxon": taxon,
            "commonName": common_names.get(taxon, taxon),
            "matchingUses": list(uses),
        }
        for taxon, uses in by_taxon.items()
    ]