import logging
import re
from models.chineseEthnobotanies import ChineseEthnobotany
logger = logging.getLogger(__name__)

async def find_plant_by_latin_name(latin_name: str) -> list[ChineseEthnobotany]:
    try:
        logger.debug(f"Searching for plants with Latin name: {latin_name}")
        pattern = re.compile(f"^{re.escape(latin_name)}$", re.IGNORECASE)
        plants = await ChineseEthnobotany.find({"latin_name": {"$regex": pattern}}).to_list()
        logger.debug(f"Plants found for Latin name '{latin_name}': {len(plants)}")
        return plants
    except Exception as e:
        logger.error(f"Error while searching for plants: {e}")
        return []


async def find_plants_by_condition(keywords: list[str]) -> list[ChineseEthnobotany]:
    try:
        regex = "|".join(re.escape(k) for k in keywords)
        plants = await ChineseEthnobotany.find(
            {"$or": [
                {"Function": {"$regex": regex, "$options": "i"}},
                {"tcmwiki_actions": {"$regex": regex, "$options": "i"}},
            ]}
        ).to_list()
        logger.debug(f"Chinese plants found for keywords {keywords}: {len(plants)}")
        return plants
    except Exception as e:
        logger.error(f"Error while searching Chinese plants by condition: {e}")
        return []

