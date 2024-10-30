from __future__ import annotations

from app.core.api_client import APIClient
from app import settings

AUTH_TOKEN_ENDPOINT = "/auth/v2/token"


def build_api_key_header(admin_api_key: str) -> dict[str, str]:
    """
    The key Secret added to the headers allows to perform operation at the admin level

    """
    return {
        "Secret": admin_api_key
    }


def build_bearer_token_header(bearer_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {bearer_token}"
    }


class OptScaleAuth:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)

    @staticmethod
    def obtain_admin_api_key(admin_api_key: str):
        return build_api_key_header(admin_api_key=admin_api_key)

    @staticmethod
    def get_bearer_token_header(bearer_token: str):
        return build_bearer_token_header(bearer_token=bearer_token)

    async def obtain_auth_token_with_user_credentials(self, email: str,
                                                      password: str) -> str | None:
        payload = {
            "password": password,
            "email": email
        }
        response = await self.api_client.post(endpoint=AUTH_TOKEN_ENDPOINT,
                                              data=payload)
        return response.get("token", None)

    async def obtain_user_auth_token_with_admin_api_key(self, user_id: str, admin_api_key: str) -> str | None:
        payload = {
            "user_id": user_id
        }
        headers = build_api_key_header(admin_api_key=admin_api_key)
        response = await self.api_client.post(endpoint=AUTH_TOKEN_ENDPOINT,
                                              headers=headers,
                                              data=payload
                                              )
        user_id_from_response = response.get("user_id", 0)
        if user_id != user_id_from_response:
            return None
        return response.get("token", None)
