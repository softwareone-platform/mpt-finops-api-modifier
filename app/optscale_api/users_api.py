from __future__ import annotations
import logging
from app.core.api_client import APIClient
from app import settings
from .auth_api import OptScaleAuth

AUTH_USERS_ENDPOINT = "/auth/v2/users"
logger = logging.getLogger("optscale_user_api")


class OptScaleUserAPI:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)
        self._auth_client = OptScaleAuth()

    # todo: check the password lenght and strength
    async def create_user(self, email: str, display_name: str, password: str) -> dict[str, str] | None:
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
                "password": password

            }
            return await self.api_client.post(endpoint=AUTH_USERS_ENDPOINT, data=payload)
        except Exception as error:
            logger.error(f"The Exception {error} occurred creating a user")
            return None

    async def get_user_by_id(self, admin_api_key: str, user_id: str) -> dict[str, str] | None:
        """

        :param admin_api_key:
        :type admin_api_key:
        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        try:
            admin_apu_key_header = self._auth_client.obtain_admin_api_key(admin_api_key=admin_api_key)

            if admin_apu_key_header is None:
                return None

            return await self.api_client.get(endpoint=AUTH_USERS_ENDPOINT + "/" + user_id,
                                             headers=admin_apu_key_header)
        except Exception as error:
            logger.error(f"The Exception {error} occurred getting the user {user_id}")
            return None
