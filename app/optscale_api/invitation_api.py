from __future__ import annotations

import logging

from fastapi import status as http_status

from app import settings
from app.core.api_client import APIClient
from app.core.exceptions import OptScaleAPIResponseError
from app.optscale_api.auth_api import (
    build_admin_api_key_header,
    build_bearer_token_header,
)

INVITATION_ENDPOINT = "/restapi/v2/invites"
logger = logging.getLogger(__name__)


class OptScaleInvitationAPI:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)

    async def decline_invitation(self, user_access_token: str, invitation_id: str):
        """
        It declines the invitation identified by the given invitation_id.
        :param invitation_id: The invitation id
        :param user_access_token: The access token of the invited user
        :return: no-content 204
        :raises: OptScaleAPIResponseError if any error occurs
        contacting the OptScale APIs
        """
        payload = {"action": "decline"}
        headers = build_bearer_token_header(bearer_token=user_access_token)
        response = await self.api_client.patch(
            endpoint=INVITATION_ENDPOINT + f"/{invitation_id}",
            data=payload,
            headers=headers,
        )
        if response.get("error"):
            logger.error("Failed to decline the invitation.")
            raise OptScaleAPIResponseError(
                title="Error response from OptScale",
                reason=response.get("data", {}).get("error", {}).get("reason", ""),
                status_code=response.get("status_code", http_status.HTTP_403_FORBIDDEN),
            )
        logger.info(f"Invitation {invitation_id} has been declined")
        return {}

    async def get_list_of_invitations(
        self, user_access_token: str | None = None, email: str | None = None
    ) -> dict[str, list[dict[str, any]]] | Exception:
        """
        It returns a list of invitations
        :param email: if provided, the invitation will be searched using the email address and
        with the Secret admin key.
        :param user_access_token: The access token of the given user
        :return:

        {"data": {
            "invites":
            [
                {
                    "deleted_at": 0,
                    "id": "f69731ee-306b-47ff-947e-2a93504922ac",
                    "created_at": 1734368623,
                    "email": "user_test_2@test.com",
                    "owner_id": "1d49c92b-60d0-457b-8d4d-6d785b677098",
                    "ttl": 1736960623,
                    "owner_name": "Dylan Dog4",
                    "owner_email": "dyland.dog6@mystery.com",
                    "organization": "My Super Cool Corp",
                    "organization_id": "f36f7e43-1eb2-4160-8bc6-06ca91fdb0bf",
                    "invite_assignments": [
                        {
                            "id": "c2fbda25-16ad-4027-ba09-908eed2485ba",
                            "scope_id": "f36f7e43-1eb2-4160-8bc6-06ca91fdb0bf",
                            "scope_type": "organization",
                            "purpose": "optscale_member",
                            "scope_name": "My Super Cool Corp"
                        }
                    ]
                }
            ]
        }
        :raises: OptScaleAPIResponseError if any error occurs
        contacting the OptScale APIs

        """
        if not user_access_token and not email:
            logger.error("Both 'user_access_token' and 'email' cannot be None.")
            raise ValueError("Both 'user_access_token' and 'email' cannot be None.")

        if email is not None:
            headers = build_admin_api_key_header(admin_api_key=settings.admin_token)
            params = {"email": email}
        else:
            headers = build_bearer_token_header(bearer_token=user_access_token)
            params = None
        response = await self.api_client.get(
            endpoint=INVITATION_ENDPOINT, headers=headers, params=params
        )
        if response.get("error"):
            logger.error("Failed to get list of invitations.")
            raise OptScaleAPIResponseError(
                title="Error response from OptScale",
                reason=response.get("data", {}).get("error", {}).get("reason", ""),
                status_code=response.get("status_code", http_status.HTTP_403_FORBIDDEN),
            )
        return response
