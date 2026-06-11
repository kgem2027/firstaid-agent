from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from beanie import init_beanie
import os

from models.user import User
from models.dd_plants import DDPlant
from models.farmacies import Farmacy
from models.ethnobotanies import Ethnobotany
from models.chemicals import Chemical
from models.session import Session
from models.unifiedEthnobotanies import UnifiedEthnobotany

_mongo_client: AsyncIOMotorClient | None = None


def get_analysis_collection() -> AsyncIOMotorCollection:
    return _mongo_client["MCP"]["analysis"]


async def connect_db():
    global _mongo_client
    mongo_uri = os.getenv("MONGO_URI")
    _mongo_client = AsyncIOMotorClient(mongo_uri)
    try:
        db = _mongo_client.get_default_database()
    except Exception:
        db = _mongo_client[os.getenv("DB_NAME", "firstaid")]
    await init_beanie(
        database=db,
        document_models=[User, DDPlant, Farmacy, Ethnobotany, Chemical, Session,
                         UnifiedEthnobotany],
    )
    print("Connected to MongoDB!")
