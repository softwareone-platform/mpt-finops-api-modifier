from __future__ import annotations

import logging

from app.core.exceptions import UserAccessTokenError
from app.optscale_api.auth_api import OptScaleAuth

logger = logging.getLogger("helper")


TOKEN_ERROR_MESSAGE = "Failed to obtain access token for user ID: {}"


def get_auth_client() -> OptScaleAuth:
    return OptScaleAuth()


async def get_user_access_token(
    user_id: str, admin_api_key: str, auth_client: OptScaleAuth
) -> str | Exception:
    try:
        # request user's access token
        user_access_token = await auth_client.obtain_user_auth_token_with_admin_api_key(
            user_id=user_id, admin_api_key=admin_api_key
        )
        logger.info(f"Successfully obtained access token for user: {user_id}")
        return user_access_token

    except UserAccessTokenError as error:
        logger.error(f"Failed to get access token for user {user_id}: {error}")
        raise
