import logging
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.core.exceptions import InvitationDoesNotExist, OptScaleAPIResponseError
from app.optscale_api.auth_api import OptScaleAuth
from app.optscale_api.invitation_api import OptScaleInvitationAPI
from app.optscale_api.users_api import OptScaleUserAPI
from tests.helpers.jwt import create_jwt_token


@pytest.fixture
def mock_register_invited():
    patcher = patch.object(OptScaleUserAPI, "create_user", new=AsyncMock())
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def mock_decline_invitation():
    patcher = patch.object(OptScaleInvitationAPI, "decline_invitation", new=AsyncMock())
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def mock_get_list_of_invitations():
    patcher = patch.object(
        OptScaleInvitationAPI, "get_list_of_invitations", new=AsyncMock()
    )
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def mock_optscale_auth_post():
    patcher = patch.object(
        OptScaleAuth, "obtain_user_auth_token_with_admin_api_key", new=AsyncMock()
    )  # noqa: E501
    mock = patcher.start()
    yield mock
    patcher.stop()


async def test_register_invited_user(
    async_client: AsyncClient,
    test_data: dict,
    mock_register_invited,
    mock_get_list_of_invitations,
):
    payload = test_data["invitation"]["case_create"]["payload"]
    mocked_response = test_data["invitation"]["case_create"]["response"]
    want = test_data["invitation"]["case_create"]["response"]["data"]
    mock_register_invited.return_value = mocked_response
    mock_get_list_of_invitations.return_value = {
        "data": {"invites": [{"field": "value"}]}
    }
    response = await async_client.post("/invitations/users", json=payload)
    assert response.status_code == 201
    got = response.json()
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"


async def test_register_invited_user_exception_handling(
    async_client: AsyncClient,
    test_data: dict,
    mock_register_invited,
    caplog,
    mock_get_list_of_invitations,
):
    mock_get_list_of_invitations.return_value = {
        "data": {"invites": [{"field": "value"}]}
    }

    # Simulate an exception in `create_user`
    mock_register_invited.side_effect = OptScaleAPIResponseError(
        title="Error response from OptScale", reason="Test Exception", status_code=403
    )

    payload = test_data["invitation"]["case_create"]["payload"]

    # Capture logs
    with caplog.at_level(logging.ERROR):
        # Send request with valid JWT token
        response = await async_client.post("/invitations/users", json=payload)

    # Verify the response status and content
    assert (
        response.status_code == 403
    ), "Expected 403 Forbidden when an exception occurs in user creation"
    got = response.json()
    assert got.get("detail").get("errors") == {"reason": "Test Exception"}
    # Verify the log entry
    assert (
        "Exception occurred during user creation: Error response from OptScale"
        in caplog.text
    ), "Expected error log message for the exception"


async def test_register_invited_user_exception_handling_invitation_not_found(
    async_client: AsyncClient,
    test_data: dict,
    mock_register_invited,
    caplog,
    mock_get_list_of_invitations,
):
    mock_get_list_of_invitations.return_value = {"data": {"invites": []}}

    payload = test_data["invitation"]["case_create"]["payload"]

    # Capture logs
    with caplog.at_level(logging.ERROR):
        # Send request with valid JWT token
        response = await async_client.post("/invitations/users", json=payload)

    # Verify the response status and content
    assert (
        response.status_code == 403
    ), "Expected 403 Forbidden when an exception occurs in user creation"
    got = response.json()
    assert got.get("detail").get("errors") == {"reason": "No details available"}
    # Verify the log entry
    assert (
        "Exception occurred during user creation: Invitation not found" in caplog.text
    ), "Expected error log message for the exception"


async def test_register_invited_user_exception_handling_invitation_doesnot_exist(
    async_client: AsyncClient,
    test_data: dict,
    mock_register_invited,
    caplog,
    mock_get_list_of_invitations,
):
    mock_get_list_of_invitations.return_value = {
        "data": {"invites": [{"field": "value"}]}
    }

    # Simulate an exception in `create_user`
    mock_register_invited.side_effect = InvitationDoesNotExist("Test Exception")

    payload = test_data["invitation"]["case_create"]["payload"]

    # Capture logs
    with caplog.at_level(logging.ERROR):
        # Send request with valid JWT token
        response = await async_client.post("/invitations/users", json=payload)

    # Verify the response status and content
    assert (
        response.status_code == 403
    ), "Expected 403 Forbidden when an exception occurs in user creation"
    got = response.json()
    assert got.get("detail").get("errors") == {"reason": "No details available"}
    # Verify the log entry
    assert (
        "There is no invitation for this email  haran.banjo@email.com"
        == caplog.messages[0]
    )
    assert (
        "Exception occurred during user creation: Test Exception" == caplog.messages[1]
    )


async def test_decline_invitation(
    async_client: AsyncClient,
    mock_decline_invitation,
    mock_optscale_auth_post,
    test_data: dict,
):
    mock_decline_invitation.return_value = {"status_code": 204}
    response = await async_client.post(
        "/invitations/users/invites/bf9f6c28-53c5-40ab-b530-4850ca5fc27f/decline",
        headers={"Authorization": "Bearer valid_user_token"},
        json={"user_id": "b57b9964-7046-4e20-812c-01ab52cf4661"},
    )  # noqa: E501
    assert response.status_code == 204
    mock_decline_invitation.assert_called_once_with(
        invitation_id="bf9f6c28-53c5-40ab-b530-4850ca5fc27f",
        user_access_token="valid_user_token",
    )


async def test_decline_invitation_handle_exception(
    async_client: AsyncClient, mock_decline_invitation, caplog, mock_optscale_auth_post
):
    mock_response = "valid_user_token"
    mock_optscale_auth_post.return_value = mock_response
    mock_decline_invitation.side_effect = OptScaleAPIResponseError(
        title="Error response from OptScale", reason="Test Exception", status_code=403
    )
    jwt_token = create_jwt_token()
    with caplog.at_level(logging.ERROR):
        # Send request with valid JWT token
        response = await async_client.post(
            "/invitations/users/invites/bf9f6c28-53c5-40ab-b530-4850ca5fc27f/decline",
            json={"user_id": "b57b9964-7046-4e20-812c-01ab52cf4661"},
            headers={"Authorization": "Bearer " + jwt_token},
        )

    # Verify the response status and content
    assert (
        response.status_code == 403
    ), "Expected 403 Forbidden when an exception occurs in user creation"
    got = response.json()
    assert got.get("detail").get("errors") == {"reason": "Test Exception"}
    # Verify the log entry
    assert (
        "Exception occurred during user creation: Error response from OptScale"
        in caplog.text
    ), "Expected error log message for the exception"
