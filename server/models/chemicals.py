from beanie import Document
from typing import List, Optional


class Chemical(Document):
    chem_id: Optional[str] = None
    name: Optional[str] = None
    casnum: Optional[str] = None
    activities: List[str] = []

    class Settings:
        name = "chemicals"
