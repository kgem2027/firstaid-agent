import logging
import re
from models.indianEthnobotanies import IndianEthnobotany
logger = logging.getLogger(__name__)

async def find_plant_by_latin_name(botanical_name: str) -> list[IndianEthnobotany]:
    try:
        logger.debug(f"Searching for plants with latin name: {botanical_name}")
        pattern = re.compile(f"^{re.escape(botanical_name)}$", re.IGNORECASE)
        plants = await IndianEthnobotany.find({"botanical_name": {"$regex": pattern}}).to_list()
        logger.debug(f"Plants found for latin name '{botanical_name}': {len(plants)}")
        return plants
    except Exception as e:
        logger.error(f"Error while searching for plants: {e}")
        return []