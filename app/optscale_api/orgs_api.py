from __future__ import annotations

import logging

from fastapi import status as http_status

from app import settings
from app.core.api_client import APIClient
from app.core.exceptions import (
    OptScaleAPIResponseError,
    UserAccessTokenError,
)
from app.core.input_validation import validate_currency
from app.optscale_api.auth_api import (
    OptScaleAuth,
    build_bearer_token_header,
)
from app.optscale_api.helpers.auth_tokens_dependency import (
    get_user_access_token,
)

ORG_ENDPOINT = "/restapi/v2/organizations"
logger = logging.getLogger(__name__)

ORG_CREATION_ERROR = "An error occurred creating an organization for user {}."

ORG_FETCHING_ERROR = "An error occurred getting organizations for user {}."


class OptScaleOrgAPI:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)

    async def get_user_org_list(self, user_access_token: str):
        """
        Returns
        :param user_access_token: The Access Token of the given user
        :return:
        """
        response = await self.api_client.get(
            endpoint=ORG_ENDPOINT,
            headers=build_bearer_token_header(bearer_token=user_access_token),
        )

        if response.get("error"):
            logger.error("Failed to get the org list from OptScale")
            raise OptScaleAPIResponseError(
                title="Error response from OptScale",
                reason=response.get("data", {}).get("error", {}).get("reason", ""),
                status_code=response.get("status_code", http_status.HTTP_403_FORBIDDEN),
            )
        logger.info(f"Successfully fetched user's org {response}")
        return response

    async def access_user_org_list_with_admin_key(
        self,
        auth_client: OptScaleAuth,
        user_id: str,
        admin_api_key: str,
    ) -> dict:
        """
        Retrieves the organization for a given user

        :param auth_client: An instance of the `OptScaleAuth` class used to interact
            with the authentication service.
        :param user_id: the user's id for whom we want to retrieve the organization
        :param admin_api_key: the secret admin API key
        :return: The organization data or None if there is an error.
        An empty list if no organization exists
        :raise:
            UserAccessTokenError If an error occurs while obtaining the access token.
            A default Exception if an error occurs accessing the organization

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
            user_access_token = await get_user_access_token(
                user_id=user_id, admin_api_key=admin_api_key, auth_client=auth_client
            )
            response = await self.get_user_org_list(user_access_token=user_access_token)
            logger.info(f"Successfully fetched user's org list {response}")
            return response

        except UserAccessTokenError as error:
            logger.error(f"Failed to get access token for user {user_id}: {error}")
            raise
        except Exception as error:
            logger.error(
                f"Exception occurred accessing an organization on OptScale: {error}"
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
    ) -> dict | Exception:
        """
        Creates a new organization for a given user

        :param auth_client: An instance of the `OptScaleAuth` class used to interact
        with the authentication service.
        :param org_name: The name of the organization
        :param currency: The currency to use
        :param user_id: The user's id for whom we want to create the organization
        :param admin_api_key: The Secret admin API key
        :return: The created organization data or None if there is an error.
        :raise:
            UserAccessTokenError If an error occurs while obtaining the access token.
            A default Exception if an error occurs accessing the organization

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
                f"Creating organization for user: {user_id} with payload {payload}"
            )
            response = await self.api_client.post(
                endpoint=ORG_ENDPOINT, headers=headers, data=payload
            )

            if response.get("error"):
                logger.error(ORG_CREATION_ERROR.format(user_id))
                raise OptScaleAPIResponseError(
                    title="Error response from OptScale",
                    reason=response.get("data", {})
                    .get("error", {})
                    .get("reason", "No details available"),  # noqa: E501
                    status_code=response.get(
                        "status_code", http_status.HTTP_403_FORBIDDEN
                    ),
                )

            logger.info(f"Successfully created organization for user: {user_id}")
            return response

        except UserAccessTokenError as error:
            logger.error(f"Failed to get access token for user {user_id}: {error}")
            raise

        except Exception as error:
            logger.error(
                f"Exception occurred creating an organization on OptScale: {error}"
            )
            raise
