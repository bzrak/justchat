from fastapi import Depends, HTTPException, Query, status
from fastapi.routing import APIRouter

from chat_server.api.deps import get_current_user
from chat_server.api.models import MessagesPublic, UserPublic, UsersPublic
from chat_server.db import crud
from chat_server.deps import DBSession

router = APIRouter(prefix="/users", tags=["dashboard-users"])


@router.get("/", response_model=UsersPublic, dependencies=[Depends(get_current_user)])
async def list_users(session: DBSession, offset: int = 0, limit: int = 10):
    """
    Get a list of users
    """

    count, users = await crud.get_users_paginated(session, offset, limit)

    return UsersPublic(count=count, users=users)


@router.get(
    "/{user_id}", response_model=UserPublic, dependencies=[Depends(get_current_user)]
)
async def get_user(session: DBSession, user_id: int):
    """
    Get user details
    """

    user = await crud.get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.get(
    "/{user_id}/messages",
    response_model=MessagesPublic,
    dependencies=[Depends(get_current_user)],
)
async def get_user_messages(
    session: DBSession, user_id: int, offset: int = 0, limit: int = 10
):
    """
    Get all messages sent by an user
    """
    user = await crud.get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    count, messages = await crud.get_user_messages(session, user_id, offset, limit)

    return MessagesPublic(count=count, messages=messages)
