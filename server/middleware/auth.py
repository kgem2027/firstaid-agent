from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

security = HTTPBearer()


async def protect(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("JWT_SECRET"),
            algorithms=["HS256"],
        )
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authorized, token failed")

        from models.user import User

        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Not authorized")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Not authorized, token failed")
