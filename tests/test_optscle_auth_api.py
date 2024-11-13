from unittest.mock import AsyncMock

import pytest

from app.optscale_api.auth_api import OptScaleAuth


@pytest.fixture
def opt_scale_auth():
    return OptScaleAuth()

@pytest.fixture
def mock_post(mocker, opt_scale_auth):
    mock_post = mocker.patch.object(opt_scale_auth.api_client, 'post', new=AsyncMock())
    return mock_post

@pytest.fixture
def mock_get(mocker, opt_scale_auth):
    mock_get = mocker.patch.object(opt_scale_auth.api_client, 'get', new=AsyncMock())
    return mock_get


@pytest.mark.asyncio(loop_scope="session")
class TestOptscaleAuthAPI:

    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        # Initialize OptScaleAPI instance
        self.opt_scale_auth = OptScaleAuth()

        # Mock the post method on the APIClient instance's client
        self.mock_post = mocker.patch.object(self.opt_scale_auth.api_client, 'post')

        self.mock_get = mocker.patch.object(self.opt_scale_auth.api_client, 'get')
        self.opt_scale_auth.build_admin_api_key_header.return_value = \
            {"Secret": "f2312f2b-46h0-4456-o0i9-58e64f2j6725"}

    async def test_user_auth_token_with_admin_api_key(self):
        mock_response = {
            "token": "MDAwZWxvY2F0aW9uIAowMDM0aWRlbnRpZmllciBmMGJkMGM0YS03YzU1LTQ1YjctOGI1OC0y"
                     "Nzc0MGUzODc4OWEKMDAyM2NpZCBjcmVhdGVkOjE3MzAxNDA3MDEuNzk3NDA5MwowMDE3Y2lkIHJlZ2l"
                     "zdGVyOkZhbHNlCjAwMWFjaWQgcHJvdmlkZXI6b3B0c2NhbGUKMDAyZnNpZ25hdHVyZSDAiphxSkvSmiZI"
                     "6eqCgqohlKYCzcKCchmHES38yC96nQo",
            "digest": "0a498f9f0aeadd67a59b93cbde528a45",
            "user_id": "f0bd0c4a-7c55-45b7-8b58-27740e38789a",
            "created_at": "2024-10-28T18:38:21",
            "valid_until": "2024-11-04T18:38:21",
            "ip": "1.2.3.4",
            "user_email": "peter.parker@iamspiderman.com"
        }
        # Define input values
        self.mock_post.return_value = mock_response
        user_token = await self.opt_scale_auth.obtain_user_auth_token_with_admin_api_key(
            user_id="f0bd0c4a-7c55-45b7-8b58-27740e38789a",
            admin_api_key="f2312f2b-46h0-4456-o0i9-58e64f2j6725"
        )
        self.mock_post.assert_called_once_with(
            endpoint="/auth/v2/token",
            headers={
                "Secret": "f2312f2b-46h0-4456-o0i9-58e64f2j6725",
            },
            data={
                "user_id": "f0bd0c4a-7c55-45b7-8b58-27740e38789a"
            }
        )
        assert user_token == mock_response.get("token")

    async def test_create_user_token(self):
        mock_response = {
            "token": "MDAwZWxvY2F0aW9uIAowMDM0aWRlbnRpZmllciBmMGJkMGM0YS03YzU1LT"
                     "Q1YjctOGI1OC0yNzc0MGUzODc4OWEKMDAyM2NpZCBjcmVhdGVkOjE3MzAxND"
                     "A3MDEuNzk3NDA5MwowMDE3Y2lkIHJlZ2lzdGVyOkZhbHNlCjAwMWFjaWQgcHJ"
                     "vdmlkZXI6b3B0c2NhbGUKMDAyZnNpZ25hdHVyZSDAiphxSkvSmiZI6eqCgqohl"
                     "KYCzcKCchmHES38yC96nQo",
            "digest": "0a498f9f0aeadd67a59b93cbde528a45",
            "user_id": "f0bd0c4a-7c55-45b7-8b58-27740e38789a",
            "created_at": "2024-10-28T18:38:21",
            "valid_until": "2024-11-04T18:38:21",
            "ip": "1.2.3.4",
            "user_email": "peter.parker@iamspiderman.com"
        }
        # Define input values
        email = "peter.parker@iamspiderman.com"
        password = "With great power comes great responsibility"
        self.mock_post.return_value = mock_response
        user_token = await self.opt_scale_auth.obtain_auth_token_with_user_credentials(
            email="peter.parker@iamspiderman.com",
            password="With great power comes great responsibility",
        )
        self.mock_post.assert_called_once_with(
            endpoint="/auth/v2/token",
            data={
                "password": password,
                "email": email
            }
        )
        assert user_token == mock_response.get("token")
