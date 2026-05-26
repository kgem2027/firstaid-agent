from beanie import Document
from typing import Optional

class ChineseEthnobotany(Document):
    Herb_en_name: Optional[str] = None
    Herb_latin_name: Optional[str] = None
    UsePart: Optional[str] = None
    Function: Optional[str] = None
    pharmacopoeia: Optional[bool] = None
    recommendable: Optional[bool] = None
    tcmwiki_processing: Optional[str] = None
    tcmwiki_harvest: Optional[str] = None
    tcmwiki_dosage: Optional[str] = None
    tcmwiki_property: Optional[str] = None
    tcmwiki_actions: Optional[str] = None
    tcmwiki_origin: Optional[str] = None
    disclaimer: Optional[str] = None

    class Settings:
        name = "Chinese Ethnobotanies"