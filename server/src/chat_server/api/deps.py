import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from chat_server.api.models import TokenContent
from chat_server.db import crud
from chat_server.db.models import UserTable
from chat_server.deps import DBSession
from chat_server.security.utils import ALGORITHM
from chat_server.settings import get_settings

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer("/api/v1/auth/login")
TokenDeps = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(session: DBSession, token: TokenDeps) -> UserTable:
    """
    Validate JWT and return the current user.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, [ALGORITHM])
        token_content = TokenContent(**payload)

        user = await crud.get_user_by_id(session, token_content.sub)

        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

        return user
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")


CurrentUser = Annotated[UserTable, Depends(get_current_user)]
