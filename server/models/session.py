from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Location(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    place_name: Optional[str] = None


class RecommendedPlant(BaseModel):
    plant_name: Optional[str] = None
    soothing_compounds: List[str] = Field(default_factory=list)
    preparation_instructions: Optional[str] = None
    safety_notes: Optional[str] = None


class Results(BaseModel):
    recommended_plants: List[RecommendedPlant] = Field(default_factory=list)
    harmful_compounds_found: List[str] = Field(default_factory=list)
    disclaimer: Optional[str] = None


class Session(Document):
    user_id: PydanticObjectId
    session_name: str = "Untitled Session"
    symptom_description: str
    photo_url: Optional[str] = None
    location: Optional[Location] = None
    results: Optional[Results] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "sessions"
