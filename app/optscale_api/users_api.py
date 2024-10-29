from __future__ import annotations

from app.core.api_client import APIClient
from app import settings
from .auth_api import OptscaleAuth

AUTH_USERS_ENDPOINT = "/auth/v2/users"


class OptScaleAPI:
    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)
        self._auth_client = OptscaleAuth()

    # todo: check the password lenght and strength
    async def create_user(self, email: str, display_name: str, password: str) -> dict[str, str] | None:
        payload = {
            "email": email,
            "display_name": display_name,
            "password": password

        }
        return await self.api_client.post(endpoint=AUTH_USERS_ENDPOINT, data=payload)

    async def get_user_by_id(self, admin_api_key: str, user_id: str) -> dict[str, str] | None:
        admin_apu_key_header = await self._auth_client.obtain_admin_api_key(admin_api_key=admin_api_key)

        if admin_apu_key_header is None:
            return None
        return await self.api_client.get(endpoint=AUTH_USERS_ENDPOINT + "/" + user_id,
                                         headers=admin_apu_key_header)
