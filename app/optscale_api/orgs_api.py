from __future__ import annotations

import logging
from app.core.api_client import APIClient
from app.core.inout_validation import validate_currency
from app import settings

from .auth_api import OptScaleAuth

ORG_ENDPOINT = "/restapi/v2/organizations"
logger = logging.getLogger("optscale_org_api")

TOKEN_ERROR_MESSAGE = "Token not found or invalid for user {}"
NO_ORG_MESSAGE = "User {} has no associated organization."
ORG_RETRIEVED_MESSAGE = "User {} is already linked to an organization."
ORG_CREATION_ERROR = "An error occurred creating an organization for user {}."


class OptScaleOrgAPI:

    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)
        self.auth_client = OptScaleAuth()

    async def get_user_org(self, user_id: str, admin_api_key: str) -> dict | None:
        """
        Retrieves the organization for a given user

        :param user_id: the user's id for whom we want to retrieve the organization
        :type user_id: string
        :param admin_api_key: the secret admin API key
        :type admin_api_key: string
        :return: The organization data or None if there is an error or no organization exists.

        """
        try:
            # request user's access token
            user_access_token = await self.auth_client.obtain_user_auth_token_with_admin_api_key(
                user_id=user_id,
                admin_api_key=admin_api_key
            )
            if user_access_token is None:
                logger.warning(TOKEN_ERROR_MESSAGE.format(user_id))
                return None
            # get the user's org
            response = await self.api_client.get(endpoint=ORG_ENDPOINT,
                                                 headers=self.auth_client._build_bearer_token_header(
                                                     bearer_token=user_access_token))
            if len(response) == 0:
                logger.info(NO_ORG_MESSAGE.format(user_id))
                return {}
            else:
                logger.info(ORG_RETRIEVED_MESSAGE.format(user_id))
                return response
        except Exception as error:
            logger.error(f"Exception occurred getting the orgs list: {error}")
            return None

    @validate_currency
    async def create_user_org(self, org_name: str, currency: str, user_id: str, admin_api_key: str) -> dict | None:
        """
        Creates a new organization for a given user

        :param org_name: the name of the organization
        :type org_name: string
        :param currency: the currency to use
        :type currency: string
        :param user_id: the user's id for whom we want to create the organization
        :type user_id: string
        :param admin_api_key: the Secret admin API key
        :type admin_api_key: string
        :return: The created organization data or None if there is an error.

        example
        {
                "deleted_at": 0,
                "created_at": 1729695339,
                "id": "dcbe83cd-18bf-4951-87aa-2764d723535b",
                "name": "MyOrg",
                "pool_id": "90991262-16ec-4246-be18-a22a31eeec57",
                "is_demo": false,
                "currency": "USD",
                "cleaned_at": 0
        }
        """
        try:
            user_access_token = await self.auth_client.obtain_user_auth_token_with_admin_api_key(
                user_id=user_id,
                admin_api_key=admin_api_key
            )
            if user_access_token is None:
                logger.warning(TOKEN_ERROR_MESSAGE.format(user_id))
                return None
            # Create the user's organization
            payload = {"name": org_name, "currency": currency}
            response = await self.api_client.post(endpoint=ORG_ENDPOINT,
                                                  headers=self.auth_client._build_bearer_token_header(
                                                      bearer_token=user_access_token,

                                                  ), data=payload)
            if not response:
                logger.error(ORG_CREATION_ERROR.format(user_id))
                return None
            return response

        except Exception as error:
            logger.error(f"Exception occurred creating an org: {error}")
            return None
