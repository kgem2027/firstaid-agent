from beanie import Document
from typing import Optional


class Ethnobotany(Document):
    fnfnum: Optional[str] = None
    taxon: Optional[str] = None
    activity: Optional[str] = None
    country: Optional[str] = None
    family: Optional[str] = None
    reference: Optional[str] = None

    class Settings:
        name = "ethnobotanies"
