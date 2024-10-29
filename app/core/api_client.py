import httpx
import logging
from typing import Any, Dict, Optional
from app import settings

logger = logging.getLogger("api_client")

API_REQUEST_TIMEOUT = settings.default_request_timeout


class APIClient:
    def __init__(self, base_url: str, timeout: int = API_REQUEST_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def _make_request(
            self, method: str, endpoint: str, headers: Optional[Dict[str, Any]] = None,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """
        This function makes an async HTTP request and handles errors.
        :param method:
        :type method:
        :param endpoint:
        :type endpoint:
        :param params:
        :type params:
        :param data:
        :type data:
        :return:
        :rtype:
        """
        try:
            response = await self.client.request(
                method=method,
                headers=headers,
                url=endpoint,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response
        except httpx.RequestError as error:
            # Handle request error (e.g., timeout or connection error)
            logger.error(f"An error occurred while requesting {error.request.url!r}.")
            raise
        except httpx.HTTPStatusError as error:
            # Handle non-2xx status codes
            logger.error(f"Error response {error.response.status_code} while requesting {error.request.url!r}.")
            raise

    async def get(self, endpoint: str, headers: Optional[Dict[str, Any]] = None,
                  params: Optional[Dict[str, Any]] = None) -> Any:
        response = await self._make_request("GET", endpoint, params=params, headers=headers)
        return response.json()

    async def post(self, endpoint: str, headers: Optional[Dict[str, Any]] = None,
                   data: Optional[Dict[str, Any]] = None) -> Any:
        response = await self._make_request("POST", endpoint, data=data, headers=headers)
        return response.json()

    async def put(self, endpoint: str, headers: Optional[Dict[str, Any]] = None,
                  data: Optional[Dict[str, Any]] = None) -> Any:
        response = await self._make_request("PUT", endpoint, data=data, headers=headers)
        return response.json()

    async def patch(self, endpoint: str, headers: Optional[Dict[str, Any]] = None,
                    data: Optional[Dict[str, Any]] = None) -> Any:
        response = await self._make_request("PATCH", endpoint, data=data, headers=headers)
        return response.json()

    async def delete(self, endpoint: str, headers: Optional[Dict[str, Any]] = None,
                     params: Optional[Dict[str, Any]] = None) -> Any:
        response = await self._make_request("DELETE", endpoint, params=params, headers=headers)
        return response.json()

    async def close(self):
        """Close the client connection."""
        await self.client.aclose()
