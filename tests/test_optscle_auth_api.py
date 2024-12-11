import logging
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.exceptions import OptScaleAPIResponseError, UserAccessTokenError
from app.optscale_api.auth_api import OptScaleAuth


@pytest.fixture
def opt_scale_auth():
    return OptScaleAuth()


@pytest.fixture
def mock_post(mocker, opt_scale_auth):
    mock_post = mocker.patch.object(opt_scale_auth.api_client, "post", new=AsyncMock())
    return mock_post


@pytest.fixture
def mock_get(mocker, opt_scale_auth):
    mock_get = mocker.patch.object(opt_scale_auth.api_client, "get", new=AsyncMock())
    return mock_get


async def test_user_auth_token_with_admin_api_key(
    async_client: AsyncClient, test_data: dict, mock_post, opt_scale_auth
):
    mock_response = test_data["auth_token"]["create"]
    mock_post.return_value = mock_response
    user_token = await opt_scale_auth.obtain_user_auth_token_with_admin_api_key(
        user_id="f0bd0c4a-7c55-45b7-8b58-27740e38789a",
        admin_api_key="f2312f2b-46h0-4456-o0i9-58e64f2j6725",
    )
    mock_post.assert_called_once_with(
        endpoint="/auth/v2/tokens",
        headers={
            "Secret": "f2312f2b-46h0-4456-o0i9-58e64f2j6725",
        },
        data={"user_id": "f0bd0c4a-7c55-45b7-8b58-27740e38789a"},
    )
    assert user_token == mock_response.get("data").get("token")


async def test_obtain_user_auth_token_with_admin_api_key_error_response(
    async_client: AsyncClient, mock_post, opt_scale_auth, caplog
):
    mock_response = {"status_code": 503, "data": {}, "error": "Connection error: Test"}
    mock_post.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(OptScaleAPIResponseError) as exc_info:
            await opt_scale_auth.obtain_user_auth_token_with_admin_api_key(
                user_id="f0bd0c4a-7c55-45b7-8b58-27740e38789a",
                admin_api_key="f2312f2b-46h0-4456-o0i9-58e64f2j6725",
            )
        exception = exc_info.value
        assert exception.title == "Error response from OptScale"
        assert exception.reason == "No details available"
        assert exception.status_code == 503
        # check the logging message printed by the obtain_user_auth_token_with_admin_api_key
        assert (
            "Failed to get an admin access token for user f0bd0c4a-7c55-45b7-8b58-27740e38789a"
            == caplog.messages[0]
        )  # noqa: E501


async def test_user_auth_token_with_not_matching_user_id(
    async_client: AsyncClient, test_data: dict, mock_post, opt_scale_auth, caplog
):
    mock_response = {
        "data": {
            "token": "MDAwZWxvY2F0aW9uIAowMDM0aWRlbnRpZmllciBmMGJkMGM0YS03YzU1LTQ1YjctOGI1OC0y"  # noqa: E501
            "Nzc0MGUzODc4OWEKMDAyM2NpZCBjcmVhdGVkOjE3MzAxNDA3MDEuNzk3NDA5MwowMDE3Y2lkIHJlZ2l"
            "zdGVyOkZhbHNlCjAwMWFjaWQgcHJvdmlkZXI6b3B0c2NhbGUKMDAyZnNpZ25hdHVyZSDAiphxSkvSmiZI"
            "6eqCgqohlKYCzcKCchmHES38yC96nQo",
            "digest": "0a498f9f0aeadd67a59b93cbde528a45",
            "user_id": "sdedds-7c55-45b7-8b58-27740e38789a",
            "created_at": "2024-10-28T18:38:21",
            "valid_until": "2024-11-04T18:38:21",
            "ip": "1.2.3.4",
            "user_email": "peter.parker@iamspiderman.com",
        },
        "status": 201,
    }
    mock_post.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(UserAccessTokenError):  # noqa: PT012
            await opt_scale_auth.obtain_user_auth_token_with_admin_api_key(
                user_id="f0bd0c4a-7c55-45b7-8b58-27740e38789a",
                admin_api_key="f2312f2b-46h0-4456-o0i9-58e64f2j6725",
            )
            # check the logging message printed by the obtain_user_auth_token_with_admin_api_key
        assert (
            "User ID mismatch: requested f0bd0c4a-7c55-45b7-8b58-27740e38789a, received sdedds-7c55-45b7-8b58-27740e38789a"  # noqa: E501
            == caplog.messages[0]
        )  # noqa: E501


async def test_user_auth_token_with_null_token(
    async_client: AsyncClient, test_data: dict, mock_post, opt_scale_auth, caplog
):
    mock_response = test_data["auth_token"]["create"]
    mock_response["data"]["token"] = None
    mock_post.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(UserAccessTokenError):  # noqa: PT012
            await opt_scale_auth.obtain_user_auth_token_with_admin_api_key(
                user_id="f0bd0c4a-7c55-45b7-8b58-27740e38789a",
                admin_api_key="f2312f2b-46h0-4456-o0i9-58e64f2j6725",
            )
            # check the logging message printed by the obtain_user_auth_token_with_admin_api_key
        assert "Token not found in the response." == caplog.messages[0]  # noqa: E501
