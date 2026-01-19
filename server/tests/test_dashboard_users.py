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
        assert data["users"][0]["username"] == "user1"
        assert data["users"][1]["username"] == "user2"

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
        assert data["users"][0]["username"] == "user2"

    @pytest.mark.asyncio
    async def test_list_users_unauthorized(self, test_client: AsyncClient):
        """
        401 is expected when no authorization is provided
        """
        response = await test_client.get(f"{API_URL}/users/")

        assert response.status_code == 401


class TestGetUser:
    """
    Tests for GET /dashboard/users/{user_id}
    """

    @pytest.mark.asyncio
    async def test_get_user_success(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """
        Get user details
        """
        user = await crud.create_user(
            test_session, UserCreate(username="testuser", password="Password1")
        )

        assert user

        response = await test_client.get(
            f"{API_URL}/users/{user.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_get_user_not_found(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """
        404 is returned for non-existent user.
        """

        # The database can't be empty otherwise the auth_headers won't work
        user = await crud.create_user(
            test_session, UserCreate(username="testuser", password="Password1")
        )

        response = await test_client.get(f"{API_URL}/users/99999", headers=auth_headers)

        assert response.status_code == 404
