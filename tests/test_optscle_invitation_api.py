from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.exceptions import OptScaleAPIResponseError
from app.optscale_api.invitation_api import OptScaleInvitationAPI

INVITATION_ENDPOINT = "/restapi/v2/invites"


@pytest.fixture
def opt_scale_invitation():
    return OptScaleInvitationAPI()


@pytest.fixture
def mock_patch(mocker, opt_scale_invitation):
    mock_post = mocker.patch.object(
        opt_scale_invitation.api_client, "patch", new=AsyncMock()
    )
    return mock_post


async def test_decline_invitation(
    async_client: AsyncClient, mock_patch, opt_scale_invitation, caplog
):
    payload = {"action": "decline"}
    mock_response = {"status_code": 204}
    mock_patch.return_value = mock_response
    await opt_scale_invitation.decline_invitation(
        user_access_token="valid user token",
        invitation_id="db540aac-451f-4288-b7b3-53e60e0a3653",
    )
    assert (
        "Invitation db540aac-451f-4288-b7b3-53e60e0a3653 has been declined"
        == caplog.messages[0]
    )
    mock_patch.assert_called_once_with(
        data=payload,
        endpoint=INVITATION_ENDPOINT + "/db540aac-451f-4288-b7b3-53e60e0a3653",
        headers={"Authorization": "Bearer valid user token"},
    )


async def test_decline_invitation_using_not_valid_invitation(
    async_client: AsyncClient, mock_patch, opt_scale_invitation, caplog
):
    payload = {"action": "decline"}
    mock_response = {
        "error": {
            "status_code": 404,
            "error_code": "OA0043",
            "reason": "Invite db540aac-451f-4288-b7b3-53e60e0a3653 not found",
            "params": ["Invite", "db540aac-451f-4288-b7b3-53e60e0a3653"],
        }
    }
    mock_patch.return_value = mock_response
    with pytest.raises(OptScaleAPIResponseError):  # noqa: PT012
        await opt_scale_invitation.decline_invitation(
            user_access_token="valid user token",
            invitation_id="db540aac-451f-4288-b7b3-53e60e0a3653",
        )
        mock_patch.assert_called_once_with(
            data=payload,
            endpoint=INVITATION_ENDPOINT + "/db540aac-451f-4288-b7b3-53e60e0a3653",
            headers={"Authorization": "Bearer valid user token"},
        )
