import pytest
import pytest_asyncio
from chat_server.db import crud


class TestGetUserByUsername:
    @pytest.mark.asyncio
    async def test_existing_user(self, test_session, user_create_obj):
        """
        Test should return an existing User.
        """
        user_data = user_create_obj
        user_db = await crud.create_user(test_session, user_data)

        assert user_db is not None, "Failure when creating a new user."

        user = await crud.get_user_by_username(test_session, user_db.username)

        assert user is not None, "A User object should have been returned."
        assert user.username == user_db.username
