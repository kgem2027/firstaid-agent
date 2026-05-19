from fastapi import APIRouter, HTTPException, Depends, Query

from middleware.auth import protect
from services import plants_service

router = APIRouter()


@router.get("/nearby")
async def nearby_plants(
    latitude: float = Query(...),
    longitude: float = Query(...),
    current_user=Depends(protect),
):
    try:
        plants = await plants_service.get_nearby_plants(latitude, longitude)
        return {"plants": plants}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
