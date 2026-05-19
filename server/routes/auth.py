from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from jose import jwt
import bcrypt
from datetime import datetime, timedelta
import os

from models.user import User
from middleware.auth import protect

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str = "User"
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str


class AuthResponse(BaseModel):
    message: str
    token: str
    user: UserOut


def generate_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=30)
    return jwt.encode({"id": str(user_id), "exp": expire}, os.getenv("JWT_SECRET"), algorithm="HS256")


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(body: RegisterRequest):
    if await User.find_one(User.email == body.email):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = bcrypt.hashpw(body.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(name=body.name, email=body.email, password=hashed)
    await user.insert()

    token = generate_token(str(user.id))
    return AuthResponse(
        message="User registered successfully",
        token=token,
        user=UserOut(id=str(user.id), name=user.name, email=user.email),
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest):
    user = await User.find_one(User.email == body.email)
    if not user or not user.match_password(body.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = generate_token(str(user.id))
    return AuthResponse(
        message="Login successful",
        token=token,
        user=UserOut(id=str(user.id), name=user.name, email=user.email),
    )


@router.get("/me")
async def me(current_user: User = Depends(protect)):
    return {
        "message": "User profile",
        "user": {"id": str(current_user.id), "name": current_user.name, "email": current_user.email},
    }
