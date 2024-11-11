from __future__ import annotations

import logging

from app import settings
from app.core.api_client import APIClient

AUTH_TOKEN_ENDPOINT = "/auth/v2/token"
logger = logging.getLogger("optscale_auth_api")


class OptScaleAuth:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)

    @staticmethod
    def build_admin_api_key_header(admin_api_key: str) -> dict[str, str]:
        """
        Builds headers with the admin API key for root-level operations
        :param admin_api_key: the secret API key
        :type admin_api_key: string
        :return: a dictionary {"Secret": "secret key here"}
        """
        return {"Secret": admin_api_key}

    @staticmethod
    def build_bearer_token_header(bearer_token: str) -> dict[str, str]:
        """
        Builds the headers with the Bearer token for user-level operations
        :param bearer_token: the Bearer token to use
        :type bearer_token: string
        :return: a dict {"Authorization": f"Bearer MYTOKENHERE"}
        """
        return {"Authorization": f"Bearer {bearer_token}"}

    async def obtain_auth_token_with_user_credentials(self, email: str,
                                                      password: str) -> str | None:
        """
        Obtains a user authentication token using user credentials
        :param email: the user's email
        :type email: string
        :param password: the user's password
        :type password: string
        :return: The authentication token if obtained successfully, otherwise None.
        """
        payload = {"password": password, "email": email}
        try:
            response = await self.api_client.post(endpoint=AUTH_TOKEN_ENDPOINT,
                                                  data=payload)
            if not response:
                logger.error("Error obtaining the user access token")
                return None
            token = response.get("token")
            if token is not None:
                return token
            logger.warning("Token not found in response when getting the user auth token.")

        except Exception as error:
            logger.error(f"Error obtaining auth token with user credentials: {error}")
        return None

    async def obtain_user_auth_token_with_admin_api_key(self, user_id: str,
                                                        admin_api_key: str) -> str | None:
        """
        Obtains an authentication token for the given user_id using the admin API key
        :param user_id: the user's ID for whom the access token will be generated
        :type user_id: string
        :param admin_api_key: the secret API key
        :type admin_api_key: string
        :return: The user authentication token if successfully obtained and verified, o
        therwise None.

        """
        payload = {"user_id": user_id}
        headers = self.build_admin_api_key_header(admin_api_key=admin_api_key)
        try:
            response = await self.api_client.post(endpoint=AUTH_TOKEN_ENDPOINT,
                                                  headers=headers,
                                                  data=payload
                                                  )
            if not response:
                logger.error("Empty response when getting the user auth token with admin API key.")
                return None
            if response.get("user_id") != user_id:
                logger.error(f"User ID mismatch: requested {user_id}, "
                             f"received {response.get('user_id')}")
                return None
            token = response.get("token")
            if token is not None:
                return token
            logger.warning("Token not found in response when getting user auth token.")

        except Exception as error:
            logger.error(f"Error obtaining user auth token with admin API key: {error}")

        return None
