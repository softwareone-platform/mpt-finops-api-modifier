import logging
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import OptScaleAPIResponseError
from app.invitations.services.external_services import remove_user, validate_user_delete
from app.optscale_api.users_api import OptScaleUserAPI

USER_ID = "f0bd0c4a-7c55-45b7-8b58-27740e38789a"
ADMIN_API_KEY = "f2312f2b-46h0-4456-o0i9-58e64f2j6725"
EMAIL = "peter.parker@iamspiderman.com"
DISPLAY_NAME = "Spider Man"
PASSWORD = "With great power comes great responsibility"


@pytest.fixture
def optscale_api():
    """Provides a clean instance of OptScaleUserAPI for each test."""
    return OptScaleUserAPI()


@pytest.fixture
def mock_post(mocker, optscale_api):
    """Mock the `post` method in `api_client`."""
    mock_post = mocker.patch.object(optscale_api.api_client, "post", new=AsyncMock())
    return mock_post


@pytest.fixture
def mock_delete(mocker, optscale_api):
    """Mock the `post` method in `api_client`."""
    mock_delete = mocker.patch.object(
        optscale_api.api_client, "delete", new=AsyncMock()
    )
    return mock_delete


@pytest.fixture
def mock_invitation_api(mocker):
    def _mock_invitation_api(return_value):
        mock = AsyncMock()
        mock.get_list_of_invitations.return_value = return_value
        mocker.patch(
            "app.optscale_api.invitation_api.OptScaleInvitationAPI", return_value=mock
        )
        return mock

    return _mock_invitation_api


@pytest.fixture
def mock_org_api(mocker):
    def _mock_org_api(return_value):
        mock = AsyncMock()
        mock.get_user_org_list.return_value = return_value
        mocker.patch(
            "app.optscale_api.orgs_api.OptScaleOrgAPI", return_value=mock_org_api
        )
        return mock

    return _mock_org_api


@pytest.fixture
def mock_user_api(mocker):
    def _mock_user_api(should_raise=False):
        mock = AsyncMock()
        if should_raise:
            mock.delete_user.side_effect = OptScaleAPIResponseError(
                title="Error response from OptScale", reason="Test", status_code=403
            )
        else:
            mock.delete_user.return_value = None
        mocker.patch("app.optscale_api.users_api.OptScaleUserAPI", return_value=mock)
        return mock

    return _mock_user_api


async def test_register_invited_user_on_optscale(caplog, optscale_api, mock_post):
    mock_response = {
        "created_at": 1730126521,
        "deleted_at": 0,
        "id": USER_ID,
        "display_name": DISPLAY_NAME,
        "is_active": True,
        "type_id": 1,
        "email": EMAIL,
        "verified": False,
        "scope_id": None,
        "slack_connected": False,
        "is_password_autogenerated": False,
        "jira_connected": False,
        "token": None,
    }
    mock_post.return_value = mock_response
    result = await optscale_api.create_user(
        email=EMAIL,
        display_name=DISPLAY_NAME,
        password=PASSWORD,
        verified=False,
        admin_api_key="test_key",
    )
    assert result == mock_response, "Expected a valid user creation response"
    log_to_verify = (
        "User successfully created: {'created_at': 1730126521, 'deleted_at': 0, 'id': "
        "'f0bd0c4a-7c55-45b7-8b58-27740e38789a', 'display_name': 'Spider Man', "
        "'is_active': True, 'type_id': 1, 'email': 'peter.parker@iamspiderman.com', "
        "'verified': False, 'scope_id': None, 'slack_connected': False, "
        "'is_password_autogenerated': False, 'jira_connected': False, 'token': None}"
    )
    assert log_to_verify == caplog.messages[0]


async def test_create_duplicate_user(caplog, optscale_api, mock_post):
    mock_response = {
        "data": {
            "error": {
                "error_code": "OA0042",
                "params": ["jerry.drake2@alphaagancy.com"],
                "reason": "User jerry.drake2@alphaagancy.com already exists",
                "status_code": 409,
            }
        },
        "error": 'HTTP error: 409 - {"error": {"status_code": 409, "error_code": "OA0042", '
        '"reason": "User jerry.drake2@alphaagancy.com already exists", '
        '"params": ["jerry.drake2@alphaagancy.com"]}}',
        "status_code": 409,
    }
    mock_post.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(  # noqa: PT012
            OptScaleAPIResponseError, match=""
        ):
            await optscale_api.create_user(
                email=EMAIL,
                display_name=DISPLAY_NAME,
                password=PASSWORD,
                admin_api_key="test_key",
            )
            mock_post.assert_called_once_with(
                endpoint="/auth/v2/users",
                data={
                    "email": EMAIL,
                    "display_name": DISPLAY_NAME,
                    "password": PASSWORD,
                },
            )
            # Verify the error log
    assert "Failed to create the requested user" in caplog.text


async def test_validate_user_delete(mock_invitation_api, mock_org_api):
    invitation_return_value = {"data": {"invites": []}}
    org_return_value = {"data": {"organizations": []}}

    invitation_api = mock_invitation_api(invitation_return_value)
    org_api = mock_org_api(org_return_value)
    user_token = "test_token"
    result = await validate_user_delete(
        user_token=user_token, invitation_api=invitation_api, org_api=org_api
    )
    assert result is True
    invitation_api.get_list_of_invitations.assert_called_once_with(
        user_access_token=user_token
    )
    org_api.get_user_org_list.assert_called_once_with(user_access_token=user_token)


async def test_validate_user_delete_false(mock_invitation_api, mock_org_api):
    invitation_return_value = {"data": {"invites": [{"field": "value"}]}}
    org_return_value = {"data": {"organizations": []}}

    invitation_api = mock_invitation_api(invitation_return_value)
    org_api = mock_org_api(org_return_value)
    user_token = "test_token"
    result = await validate_user_delete(
        user_token=user_token, invitation_api=invitation_api, org_api=org_api
    )
    assert result is False
    invitation_api.get_list_of_invitations.assert_called_once_with(
        user_access_token=user_token
    )
    org_api.get_user_org_list.assert_called_once_with(user_access_token=user_token)


async def test_validate_user_delete_exception_handling(
    caplog, mock_invitation_api, mock_org_api
):
    invitation_api = mock_invitation_api([])
    org_api = mock_org_api([])
    user_token = "test_token"
    result = await validate_user_delete(
        user_token=user_token, invitation_api=invitation_api, org_api=org_api
    )
    assert result is False
    assert (
        "Exception during deletion user validation:'list' object has no attribute 'get'"
        in caplog.messages[0]
    )
    invitation_api.get_list_of_invitations.assert_called_once_with(
        user_access_token=user_token
    )
    org_api.get_user_org_list.assert_called_once_with(user_access_token=user_token)


async def test_remove_user_success(
    caplog, mock_invitation_api, mock_org_api, mock_user_api
):
    invitation_return_value = {"data": {"invites": []}}
    org_return_value = {"data": {"organizations": []}}
    invitation_api = mock_invitation_api(invitation_return_value)
    user_api = mock_user_api(should_raise=False)
    org_api = mock_org_api(org_return_value)
    user_access_token = "test_token"
    user_id = "user_id"
    result = await remove_user(
        user_id=user_id,
        user_access_token=user_access_token,
        invitation_api=invitation_api,
        org_api=org_api,
        user_api=user_api,
    )

    assert result is True
    invitation_api.get_list_of_invitations.assert_called_once_with(
        user_access_token=user_access_token
    )
    org_api.get_user_org_list.assert_called_once_with(
        user_access_token=user_access_token
    )
    user_api.delete_user.assert_called_once_with(
        user_id=user_id, admin_api_key="f1a75f1a-36a0-4994-9d9e-36e52f1b2345"
    )


async def test_remove_user_fail(
    caplog, mock_invitation_api, mock_org_api, mock_user_api
):
    invitation_return_value = {"data": {"invites": [{"field": "value"}]}}
    org_return_value = {"data": {"organizations": []}}
    invitation_api = mock_invitation_api(invitation_return_value)
    user_api = mock_user_api(should_raise=False)
    org_api = mock_org_api(org_return_value)
    user_access_token = "test_token"
    user_id = "user_id"
    result = await remove_user(
        user_id=user_id,
        user_access_token=user_access_token,
        invitation_api=invitation_api,
        org_api=org_api,
        user_api=user_api,
    )
    assert "The user user_id cannot be deleted." == caplog.messages[0]
    assert result is False
    invitation_api.get_list_of_invitations.assert_called_once_with(
        user_access_token=user_access_token
    )
    org_api.get_user_org_list.assert_called_once_with(
        user_access_token=user_access_token
    )


async def test_remove_user_exception_handling(
    caplog, mock_invitation_api, mock_org_api, mock_user_api
):
    invitation_return_value = {"data": {"invites": []}}
    org_return_value = {"data": {"organizations": []}}
    invitation_api = mock_invitation_api(invitation_return_value)
    user_api = mock_user_api(should_raise=True)
    org_api = mock_org_api(org_return_value)
    user_access_token = "test_token"
    user_id = "user_id"
    result = await remove_user(
        user_id=user_id,
        user_access_token=user_access_token,
        invitation_api=invitation_api,
        org_api=org_api,
        user_api=user_api,
    )
    assert "Error deleting user:user_id" == caplog.messages[0]
    assert result is False
    invitation_api.get_list_of_invitations.assert_called_once_with(
        user_access_token=user_access_token
    )
    org_api.get_user_org_list.assert_called_once_with(
        user_access_token=user_access_token
    )
