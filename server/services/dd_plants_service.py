import asyncio
import logging
from models.dd_plants import DDPlant
from models.farmacies import Farmacy
from models.ethnobotanies import Ethnobotany

logger = logging.getLogger(__name__)


async def find_plant_chemicals(taxon: str) -> dict | None:
    plant, chemicals, ethnobotany = await asyncio.gather(
        DDPlant.find_one(DDPlant.taxon == taxon),
        Farmacy.find(Farmacy.taxon == taxon).to_list(),
        Ethnobotany.find(Ethnobotany.taxon == taxon).to_list(),
    )

    if not plant:
        logger.warning(f"No plant found for taxon: {taxon}")
        return None

    logger.debug(f"Plant chemicals fetched: taxon={taxon}, chemicals={len(chemicals)}")
    return {"plant": plant, "chemicals": chemicals, "ethnobotany": ethnobotany}
