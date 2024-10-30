import logging
from app.core.api_client import APIClient
from app import settings
from .auth_api import OptScaleAuth

ORG_ENDPOINT = "/restapi/v2/organizations"
logger = logging.getLogger("optscale_org_api")


class OptScaleOrgAPI:

    def __init__(self):
        self.api_client = APIClient(base_url=settings.opt_scale_api_url)
        self._auth_client = OptScaleAuth()

    async def get_user_org(self, user_id: str, admin_api_key: str):
        try:
            # request user's access token
            user_access_token = await self._auth_client.obtain_user_auth_token_with_admin_api_key(
                user_id=user_id,
                admin_api_key=admin_api_key
            )
            if user_access_token is None:
                return None
            response = await self.api_client.get(endpoint=ORG_ENDPOINT,
                                                 headers=self._auth_client.get_bearer_token_header(
                                                     bearer_token=user_access_token))
            if len(response) == 0:
                return None
            else:
                return response
        except Exception as error:
            logger.error(f"The Exception {error} occurred getting the orgs list")
            return None

    # todo: limit and validate the currency input
    async def create_user_org(self, org_name: str, currency: str, user_id: str, admin_api_key: str):
        try:
            user_access_token = await self._auth_client.obtain_user_auth_token_with_admin_api_key(
                user_id=user_id,
                admin_api_key=admin_api_key
            )
            if user_access_token is None:
                return None
            payload = {
                "name": org_name,
                "currency": currency
            }
            return await self.api_client.post(endpoint=ORG_ENDPOINT,
                                              headers=self._auth_client.get_bearer_token_header(
                                                  bearer_token=user_access_token,

                                              ), data=payload)
        except Exception as error:
            logger.error(f"The Exception {error} occurred creating an org")
            return None
