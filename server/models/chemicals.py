from beanie import Document
from pydantic import Field
from typing import List, Optional


class Chemical(Document):
    chem_id: Optional[str] = Field(None, alias="chemId")
    name: Optional[str] = None
    casnum: Optional[str] = None
    activities: List[str] = []

    model_config = {"populate_by_name": True}

    class Settings:
        name = "chemicals"
