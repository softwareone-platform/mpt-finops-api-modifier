from __future__ import annotations

import logging

from app.core.exceptions import UserAccessTokenError
from app.optscale_api.auth_api import OptScaleAuth

logger = logging.getLogger("helper")


def get_auth_client() -> OptScaleAuth:
    return OptScaleAuth()


async def get_user_access_token(
    user_id: str, admin_api_key: str, auth_client: OptScaleAuth
) -> str | Exception:
    """
    Obtains an Access Token for the given user, using the admin api key
    :param user_id: The unique identifier of the user for whom the access token
    is being requested.
    :param admin_api_key: The admin API key used for authenticating the request to
    obtain the user's token.
    :param auth_client: An instance of the `OptScaleAuth` class used to interact
    with the authentication service.
    :return: The access token for the specified user.
    :raise: UserAccessTokenError If an error occurs while obtaining the access token.
    """
    try:
        # request user's access token
        user_access_token = await auth_client.obtain_user_auth_token_with_admin_api_key(
            user_id=user_id, admin_api_key=admin_api_key
        )
        logger.info("Successfully created organization for user: %s", user_id)
        return user_access_token

    except UserAccessTokenError as error:
        logger.error("Failed to get access token for user %s: %s", user_id, error)
        raise
