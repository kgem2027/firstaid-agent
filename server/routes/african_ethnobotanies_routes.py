from fastapi import APIRouter, HTTPException, Depends, Query
from middleware.auth import protect
from services import african_ethnobotanies_service
router = APIRouter()

@router.get("/latin-name")
async def get_plants_by_latin_name(
    latin_name: str = Query(..., description="The Latin name of the plant to search for"),
    current_user=Depends(protect),
):
    res = await african_ethnobotanies_service.find_plant_by_latin_name(latin_name)
    if not res:
        raise HTTPException(status_code=404, detail=f"No plants found with Latin name: {latin_name}")
    return res
    

        