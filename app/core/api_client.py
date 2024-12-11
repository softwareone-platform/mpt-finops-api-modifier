from __future__ import annotations

import logging
import time
from typing import Any

import httpx
from httpx import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app import settings

logger = logging.getLogger(__name__)

API_REQUEST_TIMEOUT = settings.default_request_timeout


class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"Response: status_code={response.status_code}, process_time={process_time:.2f}s"
        )
        return response


class APIClient:
    def __init__(self, base_url: str, timeout: int = API_REQUEST_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> (
        Response
        | dict[str, None | str | int]
        | dict[str, str | int | Any]
        | dict[str, None | str | int]
    ):
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
                method=method, headers=headers, url=endpoint, params=params, json=data
            )
            response.raise_for_status()
            # Check if the response is JSON by inspecting the Content-Type header
            if response.headers.get("Content-Type", "").startswith("application/json"):
                try:
                    data = response.json()
                    return {"status_code": response.status_code, "data": data}
                except ValueError:
                    logger.error(
                        "Failed to parse JSON "
                        "despite Content-Type header indicating JSON."
                    )
                    return {
                        "status_code": 403,
                        "error": "Invalid JSON format in response",
                    }
            else:
                # Handle non-JSON response
                logger.warning(
                    "Response is not JSON as indicated by Content-Type header."
                )
                return {"status_code": 403, "error": "Response is not JSON"}

        except httpx.RequestError as error:
            # Log and handle connection-related errors
            logger.error(
                f"An error occurred while "
                f"requesting {error.request.url!r}. Error: {error}"
            )
            return {
                "status_code": 503,  # Service Unavailable
                "data": {},
                "error": f"Connection error: {error}",
            }
        except httpx.HTTPStatusError as error:
            # Log and handle HTTP errors (non-2xx responses)
            logger.error(
                f"Error response {error.response.status_code} "
                f"while requesting {error.request.url!r}."
            )

            return {
                "status_code": error.response.status_code,
                "data": error.response.json(),
                "error": f"HTTP error: {error.response.status_code} - {error.response.text}",
            }
        except Exception as error:
            # Catch any other unexpected errors
            logger.error(f"An unexpected error occurred: {str(error)}")
            return {
                "status_code": 500,  # Internal Server Error
                "data": {},
                "error": f"Unexpected error: {error}",
            }

    async def get(
        self,
        endpoint: str,
        headers: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        response = await self._make_request(
            "GET", endpoint, params=params, headers=headers
        )
        return response

    async def post(
        self,
        endpoint: str,
        headers: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        response = await self._make_request(
            "POST", endpoint, data=data, headers=headers
        )
        return response

    async def put(
        self,
        endpoint: str,
        headers: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        response = await self._make_request("PUT", endpoint, data=data, headers=headers)
        return response

    async def patch(
        self,
        endpoint: str,
        headers: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        response = await self._make_request(
            "PATCH", endpoint, data=data, headers=headers
        )
        return response

    async def delete(
        self,
        endpoint: str,
        headers: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        response = await self._make_request(
            "DELETE", endpoint, params=params, headers=headers
        )
        return response

    async def close(self):
        """Close the client connection."""
        await self.client.aclose()
