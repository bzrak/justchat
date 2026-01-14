from datetime import timedelta

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from chat_server.api.models import Token, UserCreate, UserLogin, UserPublic
from chat_server.db import crud
from chat_server.deps import DBSession
from chat_server.security.utils import generate_access_token, verify_password_hash

router = APIRouter(prefix="/auth", tags=["Authentication"])

ACCESS_TOKEN_EXPIRE_MIN = 15  # 15 min


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(session: DBSession, user_in: UserCreate) -> UserPublic:
    """
    Register an account.
    """
    user = await crud.create_user(session, user_in)
    if user:
        return UserPublic(id=user.id, username=user.username, is_guest=user.is_guest)
    raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists.")


@router.post("/login")
async def login(session: DBSession, credentials: UserLogin) -> Token:
    """
    Authenticate User and return a JWT Token
    """
    user = await crud.get_user_by_username(session, credentials.username)

    if not user or not verify_password_hash(credentials.password, user.hashed_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect username or password",
            {"WWW-Authenticate": "Bearer"},
        )

    access_token = generate_access_token(
        user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    )

    return Token(access_token=access_token)
