import asyncio
import logging

from fastapi import Depends

from app import settings
from app.core.exceptions import OptScaleAPIResponseError
from app.optscale_api.invitation_api import OptScaleInvitationAPI
from app.optscale_api.orgs_api import OptScaleOrgAPI
from app.optscale_api.users_api import OptScaleUserAPI

logger = logging.getLogger(__name__)


async def register_invited_user_on_optscale(
    email: str, display_name: str, password: str
):
    """

    :param email:
    :param display_name:
    :param password:
    :return:
    """
    user_api = OptScaleUserAPI()
    try:
        response = await user_api.create_user(
            email=email,
            display_name=display_name,
            password=password,
            admin_api_key=settings.admin_token,
            verified=False,
        )
        logger.info(f"Invited User successfully registered: {response}")
        return response
    except OptScaleAPIResponseError as error:
        logger.error(f"An error {error} occurred registering the invited user {email}")
        raise


async def validate_user_delete(
    user_token: str,
    invitation_api: OptScaleInvitationAPI = Depends(),
    org_api: OptScaleOrgAPI = Depends(),
) -> bool:
    """
    Validates if a user can be deleted by checking invitations and organizations.

    :param invitation_api: An instance of OptScaleInvitationAPI
    :param org_api: An instance of OptScaleOrgAPI
    :param user_token: The Access Token of the user to be deleted
    :return: True if the user has no invitations and organizations. False, otherwise
    """
    try:
        response_invitation, response_organization = await asyncio.gather(
            invitation_api.get_list_of_invitations(user_access_token=user_token),
            org_api.get_user_org_list(user_access_token=user_token),
        )
        no_org_response = {"organizations": []}
        no_invitations_response = {"invites": []}
        return (
            response_invitation.get("data", {}) == no_invitations_response
            and response_organization.get("data", {}) == no_org_response
        )
    except Exception as error:
        logger.error(f"Exception during deletion user validation:{error}")
        return False


async def remove_user(
    user_id: str,
    user_access_token: str,
    invitation_api: OptScaleInvitationAPI = Depends(),
    org_api: OptScaleOrgAPI = Depends(),
    user_api: OptScaleUserAPI = Depends(),
) -> bool:
    """
    Removes a user if they have no invitations or organizations.
    :param user_id: the user ID to be deleted
    :param user_access_token: The Access Token of the given User
    :param invitation_api: An instance of the OptScaleInvitationAPI
    :param org_api: an instance of the OptScaleOrgAPI
    :param user_api: An instance of OptScaleUserAPI
    :return: True if the user was successfully deleted, False otherwise.
    """
    validate_delete = await validate_user_delete(
        user_token=user_access_token, invitation_api=invitation_api, org_api=org_api
    )
    if validate_delete:
        try:
            await user_api.delete_user(
                user_id=user_id, admin_api_key=settings.admin_token
            )
            logger.info(f"The user {user_id} was successfully deleted")
            return True
        except OptScaleAPIResponseError:
            logger.error(f"Error deleting user:{user_id}")
            return False
    logger.info(f"The user {user_id} cannot be deleted.")
    return False
