from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy import func, select

from chat_server.api.deps import get_current_user
from chat_server.api.models import UsersPublic
from chat_server.db import crud
from chat_server.db.models import UserTable
from chat_server.deps import DBSession


router = APIRouter(prefix="/users", tags=["dashboard-users"])


@router.get("/", response_model=UsersPublic, dependencies=[Depends(get_current_user)])
async def list_users(session: DBSession):
    """
    Get a list of users
    """

    count, users = await crud.get_users_paginated(session)

    return UsersPublic(count=count, users=users)
