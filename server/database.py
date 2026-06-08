from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os

from models.user import User
from models.dd_plants import DDPlant
from models.farmacies import Farmacy
from models.ethnobotanies import Ethnobotany
from models.chemicals import Chemical
from models.session import Session
from models.unifiedEthnobotanies import UnifiedEthnobotany


async def connect_db():
    mongo_uri = os.getenv("MONGO_URI")
    client = AsyncIOMotorClient(mongo_uri)
    try:
        db = client.get_default_database()
    except Exception:
        db = client[os.getenv("DB_NAME", "firstaid")]
    await init_beanie(
        database=db,
        document_models=[User, DDPlant, Farmacy, Ethnobotany, Chemical, Session,
                         UnifiedEthnobotany],
    )
    print("Connected to MongoDB!")
