from beanie import Document
from typing import Optional


class EuropeanEthnobotany(Document):
    latin_name: Optional[str] = None
    common_name: Optional[str] = None
    botanical_name: Optional[str] = None
    therapeutic_area: Optional[str] = None
    region: Optional[str] = None
    class Settings:
        name = "European Ethnobotanies"
        