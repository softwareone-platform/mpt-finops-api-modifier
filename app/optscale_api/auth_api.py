from __future__ import annotations

import logging

from fastapi import status as http_status

from app import settings
from app.core.api_client import APIClient
from app.core.exceptions import OptScaleAPIResponseError, UserAccessTokenError

AUTH_TOKEN_ENDPOINT = "/auth/v2/tokens"
logger = logging.getLogger("optscale_auth_api")


def build_admin_api_key_header(admin_api_key: str) -> dict[str, str]:
    """
    Builds headers with the admin API key for root-level operations
    :param admin_api_key: the secret API key
    :type admin_api_key: string
    :return: a dictionary {"Secret": "secret key here"}
    """
    return {"Secret": admin_api_key}


def build_bearer_token_header(bearer_token: str) -> dict[str, str]:
    """
    Builds the headers with the Bearer token for user-level operations
    :param bearer_token: the Bearer token to use
    :type bearer_token: string
    :return: a dict {"Authorization": f"Bearer MYTOKENHERE"}
    """
    return {"Authorization": f"Bearer {bearer_token}"}


class OptScaleAuth:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)

    async def obtain_user_auth_token_with_admin_api_key(
        self, user_id: str, admin_api_key: str
    ) -> str | Exception:
        """
        Obtains an authentication token for the given user_id using the admin API key
        :param user_id: the user's ID for whom the access token will be generated
        :type user_id: string
        :param admin_api_key: the secret API key
        :type admin_api_key: string
        :return: The user authentication token if successfully obtained and verified,
        otherwise a UserAccessTokenError exception

        """
        payload = {"user_id": user_id}
        headers = build_admin_api_key_header(admin_api_key=admin_api_key)
        response = await self.api_client.post(
            endpoint=AUTH_TOKEN_ENDPOINT, headers=headers, data=payload
        )
        if response.get("error"):
            logger.error(f"Failed to get an admin access token for user {user_id}")
            raise OptScaleAPIResponseError(
                    title="Error response from OptScale",
                    reason=response.get("data", {}).get("error", {}).get("reason", ""),
                    status_code=response.get(
                        "status_code", http_status.HTTP_403_FORBIDDEN
                    ),
                )

        if response.get("data", {}).get("user_id", 0) != user_id:
            logger.error(
                f"User ID mismatch: requested {user_id}, "
                f"received {response.get('user_id')}"
            )
            raise UserAccessTokenError("Access Token User ID mismatch")
        token = response.get("data", {}).get("token")
        if token is None:
            raise UserAccessTokenError("Token not found in the response.")
        logger.info(f"Admin Access Token successfully obtained: {token}")
        return token
