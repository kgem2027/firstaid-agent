import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import connect_db
from routes import auth, location, plants, dd_plants, analyze


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield


app = FastAPI(title="FirstAid Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(location.router, prefix="/api/location", tags=["location"])
app.include_router(plants.router, prefix="/api/plants", tags=["plants"])
app.include_router(dd_plants.router, prefix="/api/ddplants", tags=["ddplants"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
