import logging
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import OptScaleAPIResponseError
from app.optscale_api.users_api import OptScaleUserAPI

USER_ID = "f0bd0c4a-7c55-45b7-8b58-27740e38789a"
INVALID_USER_ID = "f0bd0c4a-7c55-45b7-8b58-27740e38789k"
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
def mock_get(mocker, optscale_api):
    """Mock the `get` method in `api_client`."""
    mock_get = mocker.patch.object(optscale_api.api_client, "get", new=AsyncMock())
    return mock_get


@pytest.fixture
def mock_delete(mocker, optscale_api):
    """Mock the `get` method in `api_client`."""
    mock_delete = mocker.patch.object(
        optscale_api.api_client, "delete", new=AsyncMock()
    )
    return mock_delete


async def test_create_valid_user(optscale_api, mock_post, test_data: dict):
    mock_response = test_data["user"]["case_create"]["response"]
    mock_response["data"]["token"] = "valid_jwt"
    mock_post.return_value = mock_response

    response = await optscale_api.create_user(
        email=EMAIL,
        display_name=DISPLAY_NAME,
        password=PASSWORD,
        admin_api_key="test_key",
        verified=True,
    )
    got = response
    want = test_data["user"]["case_create"]["response"]
    want["data"]["token"] = "valid_jwt"
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"
    mock_post.assert_called_once_with(
        endpoint="/auth/v2/users",
        headers={"Secret": "test_key"},
        data={
            "email": EMAIL,
            "display_name": DISPLAY_NAME,
            "password": PASSWORD,
            "verified": True,
        },
    )


async def test_create_duplicate_user(caplog, optscale_api, mock_post, test_data: dict):
    mock_response = test_data["user"]["case_create"]["errors"]["409"]
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


async def test_valid_get_user_by_id(
    optscale_api, mock_get, test_data: dict, user_id=USER_ID
):
    mock_response = test_data["user"]["case_create"]["response"]
    mock_response["data"]["token"] = "valid_jwt"
    mock_get.return_value = mock_response

    response = await optscale_api.get_user_by_id(
        user_id=user_id, admin_api_key=ADMIN_API_KEY
    )
    got = response
    want = test_data["user"]["case_create"]["response"]
    want["data"]["token"] = "valid_jwt"
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"
    mock_get.assert_called_once_with(
        endpoint=f"/auth/v2/users/{user_id}", headers={"Secret": ADMIN_API_KEY}
    )


async def test_invalid_get_user_by_id(optscale_api, mock_get, user_id=INVALID_USER_ID):
    mock_response = {
        "error": {
            "status_code": 404,
            "error_code": "OA0043",
            "reason": f"Failed to get the user {INVALID_USER_ID} data from OptScale",
            "params": [user_id],
        }
    }

    mock_get.return_value = mock_response
    with pytest.raises(OptScaleAPIResponseError, match=""):  # noqa: PT012
        await optscale_api.get_user_by_id(user_id=user_id, admin_api_key=ADMIN_API_KEY)
        mock_get.assert_called_once_with(
            endpoint=f"/auth/v2/users/{user_id}", headers={"Secret": ADMIN_API_KEY}
        )


async def test_get_user_with_invalid_admin_api_key(optscale_api, mock_get):
    mock_response = {
        "error": {
            "status_code": 403,
            "error_code": "OA0006",
            "reason": "Bad secret",
            "params": [],
        }
    }
    mock_get.return_value = mock_response

    with pytest.raises(OptScaleAPIResponseError, match=""):  # noqa: PT012
        await optscale_api.get_user_by_id(user_id=USER_ID, admin_api_key="invalid_key")

        mock_get.assert_called_once_with(
            endpoint=f"/auth/v2/users/{USER_ID}", headers={"Secret": "invalid_key"}
        )


async def test_delete_user(optscale_api, mock_delete, caplog):
    mock_response = {"status_code": 204}
    mock_delete.return_value = mock_response
    await optscale_api.delete_user(user_id="user_id", admin_api_key="test_key")
    assert "User user_id successfully deleted" == caplog.messages[0]
    mock_delete.assert_called_once_with(
        endpoint="/auth/v2/users/user_id", headers={"Secret": "test_key"}
    )


async def test_delete_user_exception_handling(optscale_api, mock_delete, caplog):
    mock_response = {
        "error": {
            "status_code": 403,
            "error_code": "OA0006",
            "reason": "Bad secret",
            "params": [],
        }
    }
    mock_delete.return_value = mock_response
    with caplog.at_level(logging.ERROR):
        with pytest.raises(OptScaleAPIResponseError):
            await optscale_api.delete_user(user_id="user_id", admin_api_key="test_key")
        assert "Failed to delete the user user_id from OptScale" == caplog.messages[0]
