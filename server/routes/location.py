from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from middleware.auth import protect
from services import maps_service

router = APIRouter()


class GeocodeRequest(BaseModel):
    latitude: float
    longitude: float


@router.post("/geocode")
async def geocode(body: GeocodeRequest, current_user=Depends(protect)):
    try:
        location = await maps_service.get_location_name(body.latitude, body.longitude)
        return {"location": location}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
