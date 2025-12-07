import logging
import jwt
from chat_server.connection.user import User
from chat_server.db import crud
from chat_server.db.db import async_session
from chat_server.security.utils import ALGORITHM
from chat_server.settings import get_settings


class AuthenticationError(Exception):
    pass


class AuthenticationService:
    """
    Service for authenticating users via JWT or as Guests.
    """

    async def authenticate(self, token: str | None) -> User:
        """
        Authenticate a User via JWT Token or create a guest user with a random username.
        """
        if token is None:
            # Guest User
            return self._create_guest_user()
        else:
            # Authenticated
            return await self._authenticate_token(token)

    async def _authenticate_token(self, token: str) -> User:
        """
        Validate the JWT token and retrieve the user from database.
        """
        try:
            # Decode JWT
            payload = jwt.decode(
                token, get_settings().SECRET_KEY, algorithms=[ALGORITHM]
            )
            user_id = payload.get("sub")

            if user_id is None:
                raise AuthenticationError("Token missing 'sub'")

            # Verify User exists in database
            async with async_session() as session:
                user_db = await crud.get_user_by_id(session, user_id)
                if not user_db:
                    raise AuthenticationError(f"User {user_id} not found in database")

            return User(id=user_db.id, username=user_db.username)
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    def _create_guest_user(self) -> User:
        """
        Create a Guest User.
        """
        from random import randint

        # Ensure there will be 0 in front
        # e.g. 0024, 0432, 0002
        num = str(randint(0, 9999)).zfill(4)
        guest = User(username="Guest" + num)
        logging.info(f"Creating Guest User: {repr(guest)}")
        return guest
