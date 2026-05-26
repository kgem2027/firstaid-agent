from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import connect_db
from routes import auth, location, plants, dd_plants, analyze
from routes import african_ethnobotanies_routes, chinese_ethnobotanies_routes, european_ethnobotanies_routes, indian_ethnobotanies_routes


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
app.include_router(african_ethnobotanies_routes.router, prefix="/api/african", tags=["african"])
app.include_router(chinese_ethnobotanies_routes.router, prefix="/api/chinese", tags=["chinese"])
app.include_router(european_ethnobotanies_routes.router, prefix="/api/european", tags=["european"])
app.include_router(indian_ethnobotanies_routes.router, prefix="/api/indian", tags=["indian"])

