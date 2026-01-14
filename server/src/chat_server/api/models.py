import re
from typing import Annotated

from pydantic import BaseModel, Field, field_validator
from pydantic.types import StringConstraints

from chat_server.db.models import USERNAME_MAX_LENGTH


class UserCreate(BaseModel):
    username: Annotated[
        str, StringConstraints(True, min_length=3, max_length=USERNAME_MAX_LENGTH)
    ]
    password: str = Field(min_length=8, max_length=30)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserPublic(BaseModel):
    id: int
    username: str
    is_guest: bool


class UserLogin(BaseModel):
    username: Annotated[
        str, StringConstraints(True, min_length=3, max_length=USERNAME_MAX_LENGTH)
    ]
    password: str = Field(min_length=5, max_length=30)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
