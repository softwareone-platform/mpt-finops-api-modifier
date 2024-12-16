import logging

from app import settings
from app.core.exceptions import OptScaleAPIResponseError
from app.optscale_api.users_api import OptScaleUserAPI

logger = logging.getLogger(__name__)


async def register_invited_user_on_optscale(
    email: str, display_name: str, password: str
):
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
