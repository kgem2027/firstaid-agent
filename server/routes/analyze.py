from fastapi import APIRouter, File, UploadFile, Form, Depends
from services.remedy_service import find_remedies
from middleware.auth import protect
from models.user import User

router = APIRouter()

@router.post("/")
async def analyze_route(
    image: UploadFile = File(...),
    symptoms: str = Form(...),
    country: str = Form(...),
    current_user: User = Depends(protect),
):
    image_bytes = await image.read()
    result = await find_remedies(image_bytes, symptoms, country, str(current_user.id))
    return result
