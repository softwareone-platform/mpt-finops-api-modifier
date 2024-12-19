import logging
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
    mock_patch = mocker.patch.object(
        opt_scale_invitation.api_client, "patch", new=AsyncMock()
    )
    return mock_patch


@pytest.fixture
def mock_get(mocker, opt_scale_invitation):
    mock_get = mocker.patch.object(
        opt_scale_invitation.api_client, "get", new=AsyncMock()
    )
    return mock_get


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


async def test_get_list_of_invitations(
    async_client: AsyncClient, mock_get, opt_scale_invitation, caplog
):
    mock_response = {
        "invites": [
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
                        "scope_name": "My Super Cool Corp",
                    }
                ],
            }
        ]
    }
    mock_get.return_value = mock_response
    response = await opt_scale_invitation.get_list_of_invitations(
        user_access_token="user_token"
    )
    assert response == mock_response


async def test_get_list_of_invitations_error(
    async_client: AsyncClient, mock_get, opt_scale_invitation, caplog
):
    mock_response = {
        "status_code": 403,
        "data": {
            "error": {
                "status_code": 403,
                "error_code": "OA0042",
                "reason": "Test",
            }
        },
        "error": 'HTTP error: 403 - {"error": {"status_code": 403, "error_code": "OA0042",'  # noqa: E501
        '"reason": "Test"}}',
    }
    mock_get.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(OptScaleAPIResponseError):  # noqa: PT012
            await opt_scale_invitation.get_list_of_invitations(
                user_access_token="user_token"
            )
        assert "Failed to get list of invitations." == caplog.messages[0]
