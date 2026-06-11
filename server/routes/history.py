from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any

from middleware.auth import protect
from models.user import User
from database import get_analysis_collection

router = APIRouter()


class AnalysisRecord(BaseModel):
    id: str
    symptoms: str
    country: str
    condition: str
    compoundKeywords: list[str]
    remedyPlants: list[Any]


@router.get("/", response_model=list[AnalysisRecord])
async def get_history(current_user: User = Depends(protect)):
    collection = get_analysis_collection()
    cursor = collection.find(
        {"user_id": str(current_user.id)},
        sort=[("_id", -1)],
    )
    records = []
    async for doc in cursor:
        records.append(AnalysisRecord(
            id=str(doc["_id"]),
            symptoms=doc.get("symptoms", ""),
            country=doc.get("country", ""),
            condition=doc.get("condition", ""),
            compoundKeywords=doc.get("compoundKeywords", []),
            remedyPlants=doc.get("remedyPlants", []),
        ))
    return records
