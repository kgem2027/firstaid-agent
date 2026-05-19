from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import List
import bcrypt
from datetime import datetime


class User(Document):
    name: str = "User"
    email: str
    password: str
    sessions: List[PydanticObjectId] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

    def match_password(self, entered_password: str) -> bool:
        return bcrypt.checkpw(entered_password.encode("utf-8"), self.password.encode("utf-8"))
