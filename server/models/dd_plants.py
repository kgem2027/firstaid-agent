from beanie import Document
from typing import List, Optional


class DDPlant(Document):
    fnfnum: Optional[str] = None
    taxon: Optional[str] = None
    genus: Optional[str] = None
    species: Optional[str] = None
    family: Optional[str] = None
    common_names: List[str] = []

    class Settings:
        name = "plants"
