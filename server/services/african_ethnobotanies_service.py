import logging
from models.africanEthnobotanies import AfricanEthnobotany
import re

logger = logging.getLogger(__name__)

async def find_plant_by_latin_name(latin_name: str) -> list[AfricanEthnobotany]:
    try:
        logger.debug(f"Searching for plants with Latin name: {latin_name}")
        pattern = re.compile(f"^{re.escape(latin_name)}$", re.IGNORECASE)
        plants = await AfricanEthnobotany.find({"latin_name": {"$regex": pattern}}).to_list()
        logger.debug(f"Plants found for Latin name '{latin_name}': {len(plants)}")
        return plants
    except Exception as e:
        logger.error(f"Error while searching for plants: {e}")
        return []


async def find_plants_by_condition(keywords: list[str]) -> list[AfricanEthnobotany]:
    try:
        regex = "|".join(re.escape(k) for k in keywords)
        plants = await AfricanEthnobotany.find(
            {"health_problems": {"$regex": regex, "$options": "i"}}
        ).to_list()
        logger.debug(f"African plants found for keywords {keywords}: {len(plants)}")
        return plants
    except Exception as e:
        logger.error(f"Error while searching African plants by condition: {e}")
        return []
