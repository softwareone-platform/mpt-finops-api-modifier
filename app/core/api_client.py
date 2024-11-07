import httpx
import logging
from typing import Any, Dict, Optional

from httpx import Response

from app import settings

logger = logging.getLogger("api_client")

API_REQUEST_TIMEOUT = settings.default_request_timeout


class APIClient:
    def __init__(self, base_url: str, timeout: int = API_REQUEST_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout,
                                        verify=False)  # todo: check this verify

    async def _make_request(
            self, method: str, endpoint: str, headers: Optional[Dict[str, Any]] = None,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None
    ) -> Response | dict[str, None | str | int] | dict[str, str | int | Any] | dict[str, None | str | int]:
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
            # Check if the response is JSON by inspecting the Content-Type header
            if response.headers.get("Content-Type") == "application/json":
                try:
                    data = response.json()
                    return {"status_code": response.status_code, "data": data}
                except ValueError:
                    logger.error("Failed to parse JSON despite Content-Type header indicating JSON.")
                    return {"status_code": response.status_code, "error": "Invalid JSON format in response"}
            else:
                # Handle non-JSON response
                logger.warning("Response is not JSON as indicated by Content-Type header.")
                return {"status_code": response.status_code, "error": response.text}

        except httpx.RequestError as error:
            # Log and handle connection-related errors
            logger.error(f"An error occurred while requesting {error.request.url!r}. Error: {str(error)}")
            return {
                "status_code": 503,  # Service Unavailable
                "data": None,
                "error": f"Connection error: {str(error)}"
            }
        except httpx.HTTPStatusError as error:
            # Log and handle HTTP errors (non-2xx responses)
            logger.error(f"Error response {error.response.status_code} while requesting {error.request.url!r}.")
            return {
                "status_code": error.response.status_code,
                "data": error.response.json(),
                "error": f"HTTP error: {error.response.status_code} - {error.response.text}"
            }
        except Exception as error:
            # Catch any other unexpected errors
            logger.error(f"An unexpected error occurred: {str(error)}")
            return {
                "status_code": 500,  # Internal Server Error
                "data": None,
                "error": f"Unexpected error: {str(error)}"
            }

    async def get(self, endpoint: str, headers: Optional[Dict[str, Any]] = None,
                  params: Optional[Dict[str, Any]] = None) -> Any:
        response = await self._make_request("GET", endpoint, params=params, headers=headers)
        return response

    async def post(self, endpoint: str, headers: Optional[Dict[str, Any]] = None,
                   data: Optional[Dict[str, Any]] = None) -> Any:
        response = await self._make_request("POST", endpoint, data=data, headers=headers)
        return response

    async def put(self, endpoint: str, headers: Optional[Dict[str, Any]] = None,
                  data: Optional[Dict[str, Any]] = None) -> Any:
        response = await self._make_request("PUT", endpoint, data=data, headers=headers)
        return response

    async def patch(self, endpoint: str, headers: Optional[Dict[str, Any]] = None,
                    data: Optional[Dict[str, Any]] = None) -> Any:
        response = await self._make_request("PATCH", endpoint, data=data, headers=headers)
        return response

    async def delete(self, endpoint: str, headers: Optional[Dict[str, Any]] = None,
                     params: Optional[Dict[str, Any]] = None) -> Any:
        response = await self._make_request("DELETE", endpoint, params=params, headers=headers)
        return response

    async def close(self):
        """Close the client connection."""
        await self.client.aclose()
