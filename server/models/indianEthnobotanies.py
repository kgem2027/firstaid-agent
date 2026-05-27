from beanie import Document
from typing import Optional

class IndianEthnobotany(Document):
    herb_name: Optional[str] = None
    common_name: Optional[str] = None
    part_used: Optional[str] = None
    botanical_name: Optional[str] = None
    english_name: Optional[str] = None
    dose: Optional[str] = None
    therapeutic_uses: Optional[str] = None

    class Settings:
        name = "Indian Ethnobotanies"