from fastapi import APIRouter, File, UploadFile, Form
from services.remedy_service import find_remedies

router = APIRouter()

@router.post("/")
async def analyze_route(
    image: UploadFile = File(...),
    symptoms: str = Form(...),
    country: str = Form(...),
):
    image_bytes = await image.read()
    result = await find_remedies(image_bytes, symptoms, country)
    return result
