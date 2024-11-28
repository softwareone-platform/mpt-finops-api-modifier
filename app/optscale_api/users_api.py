from __future__ import annotations

import logging

from app import settings
from app.core.api_client import APIClient
from app.core.exceptions import UserCreationError

from .auth_api import build_admin_api_key_header

AUTH_USERS_ENDPOINT = "/auth/v2/users"
logger = logging.getLogger("optscale_user_api")


class OptScaleUserAPI:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)

    # todo: check the password lenght and strength
    async def create_user(
        self, email: str, display_name: str, password: str
    ) -> dict[str, str] | None:
        """
        Creates a new user in the system.

        :param email: The email of the user.
        :type email: string
        :param display_name: The display name of the user
        :type display_name: string
        :param password: The password of the user.
        :type password: string
        :return:dict[str, str] | None: User information if successful; otherwise, None.
        """
        try:
            payload = {
                "email": email,
                "display_name": display_name,
                "password": password,
            }
            response = await self.api_client.post(
                endpoint=AUTH_USERS_ENDPOINT, data=payload
            )
            if not response:
                logger.error("User creation failed. No response received.")
            return response
        except Exception as error:
            logger.error(
                f"An unexpected error occurred while creating the user: {error}"
            )
            raise UserCreationError(
                "An unexpected error occurred while creating the user."
            ) from error

    async def get_user_by_id(
        self, admin_api_key: str, user_id: str
    ) -> dict[str, str] | None:
        """
        Retrieves a user's information

        :param admin_api_key: the secret admin API key
        :type admin_api_key: string
        :param user_id: the user's ID for whom we want to retrieve the information
        :type user_id: string
        :return: a dict with the user's information if found. Otherwise, None
        example
        {
            "created_at": 1730126521,
            "deleted_at": 0,
            "id": "f0bd0c4a-7c55-45b7-8b58-27740e38789a",
            "display_name": "Spider Man",
            "is_active": True,
            "type_id": 1,
            "email": "peter.parker@iamspiderman.com",
            "scope_id": None,
            "slack_connected": False,
            "is_password_autogenerated": False,
            "jira_connected": False,
            "scope_name": None
        }

        """
        try:
            headers = build_admin_api_key_header(admin_api_key=admin_api_key)
            response = await self.api_client.get(
                endpoint=AUTH_USERS_ENDPOINT + "/" + user_id, headers=headers
            )
            if not response:
                logger.info(f"No data returned for the user {user_id}")
            return response
        except Exception as error:
            logger.error(
                f"Exception occurred getting the information for the user: "
                f"{user_id} - {error}"
            )
            return None
