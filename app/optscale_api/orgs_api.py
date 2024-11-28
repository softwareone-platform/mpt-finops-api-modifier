from __future__ import annotations

import logging

from fastapi import status as http_status

from app import settings
from app.core.api_client import APIClient
from app.core.exceptions import (
    OptScaleAPIResponseError,
    UserAccessTokenError,
    UserOrgCreationError,
)
from app.core.inout_validation import validate_currency
from app.optscale_api.auth_api import (
    OptScaleAuth,
    build_bearer_token_header,
)
from app.optscale_api.helpers.auth_tokens_dependency import (
    get_user_access_token,
)

ORG_ENDPOINT = "/restapi/v2/organizations"
logger = logging.getLogger("optscale_org_api")

TOKEN_ERROR_MESSAGE = "Failed to obtain access token for user ID: {}"
ORG_CREATION_ERROR = "An error occurred creating an organization for user {}."

ORG_FETCHING_ERROR = "An error occurred getting organizations for user {}."


class OptScaleOrgAPI:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)

    async def get_user_org(
        self, user_id: str, admin_api_key: str, auth_client: OptScaleAuth
    ) -> dict:
        """
        Retrieves the organization for a given user

        :param auth_client:
        :type auth_client:
        :param user_id: the user's id for whom we want to retrieve the organization
        :type user_id: string
        :param admin_api_key: the secret admin API key
        :type admin_api_key: string
        :return: The organization data or None if there is an error.
        An empty list if no organization exists
        The Optscale API returns a list or dict like the following one:
        {
            "organizations": [
                {
                    "deleted_at": 0,
                    "created_at": 1731919809,
                    "id": "3e61c772-b78a-4345-b7da-5243b09bfe03",
                    "name": "MyOrg",
                    "pool_id": "0bc61f62-f280-4a03-bf3f-446b14994594",
                    "is_demo": false,
                    "currency": "USD",
                    "cleaned_at": 0
                }
            ]
        }
        """
        try:
            # get the user's org
            user_access_token = await get_user_access_token(
                user_id=user_id, admin_api_key=admin_api_key, auth_client=auth_client
            )
            response = await self.api_client.get(
                endpoint=ORG_ENDPOINT,
                headers=build_bearer_token_header(bearer_token=user_access_token),
            )

            if response.get("error"):
                logger.error(
                    f"Failed to get the org from Server, for the user : {user_id}"
                )
                raise OptScaleAPIResponseError(
                    title="Error response from OptScale",
                    reason=response.get("data", {}).get("error", {}).get("reason", ""),
                    status_code=response.get(
                        "status_code", http_status.HTTP_403_FORBIDDEN
                    ),
                )

            return response

        except UserAccessTokenError as error:
            logger.error(f"Failed to get access token for user {user_id}: {error}")
            raise

        except OptScaleAPIResponseError as error:
            logger.error(f"Failed to get access token for user {user_id}: {error}")
            raise

        except Exception as error:
            logger.error(
                f"Unexpected error retrieving organizations for {user_id}: {error}"
            )
            raise

    @validate_currency
    async def create_user_org(
        self,
        org_name: str,
        currency: str,
        user_id: str,
        admin_api_key: str,
        auth_client: OptScaleAuth,
    ) -> dict | None:
        """
        Creates a new organization for a given user

        :param auth_client:
        :type auth_client:
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
            logger.info(f"Fetching access token for user: {user_id}")
            user_access_token = await get_user_access_token(
                user_id=user_id, admin_api_key=admin_api_key, auth_client=auth_client
            )
            # Create the user's organization
            payload = {"name": org_name, "currency": currency}
            headers = build_bearer_token_header(bearer_token=user_access_token)
            logger.info(
                f"Creating organization for user: {user_id} with payload: {payload}"
            )
            response = await self.api_client.post(
                endpoint=ORG_ENDPOINT, headers=headers, data=payload
            )
            if not response:
                logger.error(ORG_CREATION_ERROR.format(user_id))
                raise UserOrgCreationError(
                    f"Organization creation failed for user: {user_id}"
                )

            logger.info(f"Successfully created organization for user: {user_id}")
            return response
        except UserAccessTokenError as auth_error:
            logger.error(
                f"Access token error while creating an org for the user: "
                f"{user_id}: {auth_error}"
            )
            raise
        except UserOrgCreationError as org_error:
            logger.error(
                f"Organization creation error for user: {user_id} - {org_error}"
            )
            raise

        except Exception as error:
            logger.error(
                f"Exception occurred creating an org for the user: {user_id} - {error}"
            )
            raise

    # async def add_cloud_account(self,cloud_account_conf:dict[str, str], org_id:str, user_id:str,
    #                             admin_api_key:str):
    #     try:
    #
    #         # todo: validate the cloud_account_conf
    #         # request user's access token
    #         user_access_token = await self.auth_client.obtain_user_auth_token_with_admin_api_key(
    #             user_id=user_id,
    #             admin_api_key=admin_api_key
    #         )
    #         if user_access_token is None:
    #             logger.warning(TOKEN_ERROR_MESSAGE.format(user_id))
    #             return None
    #
    #
    #     except Exception as error:
    #         logger.error(f"Exception occurred adding a
    #         cloud account to the org {org_id}: {error}")
    #         return None
