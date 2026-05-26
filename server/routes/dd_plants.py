from fastapi import APIRouter, HTTPException, Depends, Query

from middleware.auth import protect
from services import dd_plants_service
from models.dd_plants import DDPlant

router = APIRouter()




@router.get("/chemicals")
async def plant_chemicals(
    taxon: str = Query(...),
    current_user=Depends(protect),
):
    try:
        result = await dd_plants_service.find_plant_chemicals(taxon)
        if result is None:
            raise HTTPException(status_code=404, detail=f"No plant found for taxon: {taxon}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-location")
async def plants_by_location(
    country: str = Query(...),
    current_user=Depends(protect),
):
    try:
        plants = await dd_plants_service.find_plant_by_location(country)
        if plants is None or len(plants) == 0:
            raise HTTPException(status_code=404, detail=f"No plants found for country: {country}")
        return plants
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))