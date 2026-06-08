import logging
from models.unifiedEthnobotanies import UnifiedEthnobotany
from services.embedding_service import embed_query

logger = logging.getLogger(__name__)

_VECTOR_INDEX = "unified_vector_search"


async def find_plants_by_region(
    keywords: list[str],
    region: str,
    safe_use_types: list[str] | None = None,
    exclude_use_types: list[str] | None = None,
) -> list[UnifiedEthnobotany]:
    try:
        query_vector = await embed_query(" ".join(keywords))
        collection = UnifiedEthnobotany.get_motor_collection()

        cursor = collection.aggregate([
            {
                "$vectorSearch": {
                    "index": _VECTOR_INDEX,
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 200,
                    "limit": 60,
                    "filter": {"region": {"$eq": region}},
                }
            },
            {"$project": {"embedding": 0}},
        ])
        raw = await cursor.to_list(length=None)

        exclude_set = {s.lower() for s in (exclude_use_types or [])}
        safe_set = {s.lower() for s in (safe_use_types or [])}

        plants = []
        for doc in raw:
            use_type = (doc.get("use_type") or "").lower()
            if exclude_set and use_type in exclude_set:
                continue
            if safe_set and use_type and use_type not in safe_set:
                continue
            plants.append(UnifiedEthnobotany(
                region=doc.get("region", region),
                latin_name=doc.get("latin_name"),
                common_name=doc.get("common_name"),
                part_used=doc.get("part_used"),
                preparation=doc.get("preparation"),
                health_problems=doc.get("health_problems"),
                therapeutic_area=doc.get("therapeutic_area"),
                therapeutic_uses=doc.get("therapeutic_uses"),
                function=doc.get("function"),
                tcmwiki_actions=doc.get("tcmwiki_actions"),
                dose=doc.get("dose"),
                tcmwiki_dosage=doc.get("tcmwiki_dosage"),
                use_type=doc.get("use_type"),
                category=doc.get("category"),
                description=doc.get("description"),
            ))

        logger.debug(f"Unified [{region}] plants found for {keywords}: {len(plants)}")
        return plants
    except Exception as e:
        logger.error(f"Error searching unified ethnobotanies [{region}]: {e}")
        return []
