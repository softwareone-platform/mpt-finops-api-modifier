import logging
from unittest.mock import AsyncMock

import pytest

from app.optscale_api.orgs_api import OptScaleOrgAPI

ORG_RESPONSE = {
    "deleted_at": 0,
    "created_at": 1729695339,
    "id": "dcbe83cd-18bf-4951-87aa-2764d723535b",
    "name": "MyOrg",
    "pool_id": "90991262-16ec-4246-be18-a22a31eeec57",
    "is_demo": False,
    "currency": "USD",
    "cleaned_at": 0
}


@pytest.fixture
def optscale_api():
    return OptScaleOrgAPI()


@pytest.fixture
def mock_post(mocker, optscale_api):
    mock_post = mocker.patch.object(optscale_api.api_client, 'post', new=AsyncMock())
    return mock_post


@pytest.fixture
def mock_get(mocker, optscale_api):
    mock_get = mocker.patch.object(optscale_api.api_client, 'get', new=AsyncMock())
    return mock_get


@pytest.fixture
def mock_auth_token(mocker, optscale_api):
    mock_auth_token = mocker.patch.object(optscale_api.auth_client,
                                          'obtain_user_auth_token_with_admin_api_key',
                                          return_value="good token")
    return mock_auth_token


@pytest.fixture
def mock_invalid_auth_token(mocker, optscale_api):
    mock_auth_token = mocker.patch.object(optscale_api.auth_client,
                                          'obtain_user_auth_token_with_admin_api_key',
                                          return_value=None)
    return mock_auth_token



async def test_create_user_org(optscale_api, mock_post, mock_auth_token):
    mock_post.return_value = ORG_RESPONSE

    result = await optscale_api.create_user_org(org_name="MyOrg",
                                                    currency="USD",
                                                    user_id="test_user",
                                                    admin_api_key="test_key")

    assert result == ORG_RESPONSE
    # Assert that mock_post was called with expected arguments
    mock_post.assert_called_once_with(
        endpoint="/restapi/v2/organizations",
         data={
                "name": "MyOrg",
                "currency": "USD"
        },
            headers={"Authorization": "Bearer good token"}
        )

async def test_create_user_org_with_invalid_currency(caplog, optscale_api, mock_post,
                                                     mock_auth_token):
    with caplog.at_level(logging.ERROR):
        result = await optscale_api.create_user_org(org_name="Test Org",
                                                        currency="not valid currency",
                                                        user_id="test_user",
                                                        admin_api_key="test_key")

        assert result is None, "Expected None for invalid currency"
        assert "Invalid currency: not valid currency" in caplog.text , ("Expected error message for"
                                                                        " invalid currency")

async def test_get_user_org_with_no_token(optscale_api, mock_post, mock_invalid_auth_token):
    result = await optscale_api.create_user_org(org_name="MyOrg",
                                                    currency="USD",
                                                    user_id="test_user",
                                                    admin_api_key="test_key")

    assert result is None, "Expected None when token is invalid"

async def test_get_user_org_empty_response( optscale_api, mock_get, mock_auth_token):
    mock_get.return_value = {}
    result = await optscale_api.get_user_org(
            user_id="test_user", admin_api_key="test_key"
    )
    assert result == {}, "Expected an empty response when org is not found"
    mock_get.assert_called_once_with(
        endpoint="/restapi/v2/organizations",
        headers={"Authorization": "Bearer good token"}
    )
