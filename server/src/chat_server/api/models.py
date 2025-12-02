from typing import Annotated
from pydantic import BaseModel, Field
from pydantic.types import StringConstraints

from chat_server.db.models import USERNAME_MAX_LENGTH


class UserCreate(BaseModel):
    username: Annotated[
        str, StringConstraints(True, min_length=3, max_length=USERNAME_MAX_LENGTH)
    ]
    password: str = Field(min_length=6, max_length=30)


class UserLogin(BaseModel):
    username: Annotated[
        str, StringConstraints(True, min_length=3, max_length=USERNAME_MAX_LENGTH)
    ]
    password: str = Field(min_length=6, max_length=30)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenContent(BaseModel):
    sub: int | None = None
