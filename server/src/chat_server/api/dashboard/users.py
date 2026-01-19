from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from chat_server.api.deps import get_current_user
from chat_server.api.models import MessagesPublic, UserPublic, UserUpdate, UsersPublic
from chat_server.db import crud
from chat_server.deps import DBSession

router = APIRouter(prefix="/users", tags=["dashboard-users"])


@router.get("/", response_model=UsersPublic, dependencies=[Depends(get_current_user)])
async def list_users(session: DBSession, offset: int = 0, limit: int = 10):
    """
    Get a list of users
    """

    count, users = await crud.get_users_paginated(session, offset, limit)

    return UsersPublic(count=count, users=users)  # type: ignore


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

    return MessagesPublic(count=count, messages=messages)  # type: ignore


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
    dependencies=[Depends(get_current_user)],
)
async def update_user(session: DBSession, user_id: int, user_in: UserUpdate):
    """
    Update user details
    """
    try:
        user = await crud.update_user(session, user_id, user_in)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        return user
    except ValueError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username in use")
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "An internal server error occurred. Try again.",
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def delete_user(session: DBSession, user_id: int):
    """
    Delete user
    """
    await crud.delete_user_by_id(session, user_id)
