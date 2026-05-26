import logging
import re
from models.chineseEthnobotanies import ChineseEthnobotany
logger = logging.getLogger(__name__)

async def find_plant_by_latin_name(Herb_latin_name: str) -> list[ChineseEthnobotany]:
    try:
        logger.debug(f"Searching for plants with Latin name: {Herb_latin_name}")
        pattern = re.compile(f"^{re.escape(Herb_latin_name)}$", re.IGNORECASE)
        plants = await ChineseEthnobotany.find({"Herb_latin_name": {"$regex": pattern}}).to_list()
        logger.debug(f"Plants found for Latin name '{Herb_latin_name}': {len(plants)}")
        return plants
    except Exception as e:
        logger.error(f"Error while searching for plants: {e}")
        return []
     
