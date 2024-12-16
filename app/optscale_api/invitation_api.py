from __future__ import annotations

import logging

from fastapi import status as http_status

from app import settings
from app.core.api_client import APIClient
from app.core.exceptions import OptScaleAPIResponseError
from app.optscale_api.auth_api import build_bearer_token_header

INVITATION_ENDPOINT = "/restapi/v2/invites"
logger = logging.getLogger(__name__)


class OptScaleInvitationAPI:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)

    async def decline_invitation(self, user_access_token: str, invitation_id: str):
        """

        :param invitation_id:
        :type invitation_id:
        :param user_access_token:
        :return:
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
        return response
