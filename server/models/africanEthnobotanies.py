from beanie import Document
from typing import Optional

class AfricanEthnobotany(Document):
    latin_name: Optional[str] = None
    countries: Optional[str] = None
    health_problems: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None

    class Settings:
        name = "African Ethnobotanies"