import pytest
from httpx import AsyncClient, head

from chat_server.api.models import UserCreate
from chat_server.db import crud

API_URL = "/api/v1/dashboard"


class TestListUsers:
    """
    Tests for GET /dashboard/users/
    """

    @pytest.mark.asyncio
    async def test_list_users_success(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        await crud.create_user(
            test_session, UserCreate(username="user1", password="Password1")
        )
        await crud.create_user(
            test_session, UserCreate(username="user2", password="Password2")
        )

        response = await test_client.get(f"{API_URL}/users/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert data["users"][0].get("username") == "user1"
        assert data["users"][1].get("username") == "user2"

    @pytest.mark.asyncio
    async def test_list_users_pagination(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """
        Test if pagination works
        """
        for i in range(6):
            await crud.create_user(
                test_session, UserCreate(username=f"user{i}", password=f"Password{i}")
            )

        response = await test_client.get(
            f"{API_URL}/users/?offset=2&limit=2", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 6
        assert len(data["users"]) == 2
        assert data["users"][0].get("username") == "user2"

    @pytest.mark.asyncio
    async def test_list_users_unauthorized(self, test_client: AsyncClient):
        """
        401 is expected when no authorization is provided
        """
        response = await test_client.get(f"{API_URL}/users/")

        assert response.status_code == 401
