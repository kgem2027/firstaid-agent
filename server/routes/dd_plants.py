from fastapi import APIRouter, HTTPException, Depends, Query

from middleware.auth import protect
from services import dd_plants_service

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
