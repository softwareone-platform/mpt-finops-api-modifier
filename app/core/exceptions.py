from __future__ import annotations

import logging
from typing import NoReturn

from fastapi import HTTPException
from fastapi import status as http_status

from app.core.error_formats import create_error_response

logger = logging.getLogger("api.exception")


class UserCreationError(Exception):
    """Custom exception for errors during user creation."""

    pass


class UserAccessTokenError(Exception):
    """Custom exception for errors during user access token creation."""

    pass


class UserOrgCreationError(Exception):
    """Custom exception for errors during user access token creation."""

    pass


class CurrencyError(Exception):
    """Custom exception for errors during user access token creation."""

    pass


class OptScaleAPIResponseError(Exception):
    def __init__(self, status_code: int, title: str, reason: str):
        message = f"{title}"
        super().__init__(message)
        self.status_code = status_code
        self.title = title
        self.reason = reason


def handle_exception(error: HTTPException | Exception) -> NoReturn:
    """
    Handles exceptions during user creation by logging the error and raising an
    appropriate HTTP response.

    If the error is an instance of `HTTPException`, it re-raises the exception.
    Otherwise, it raises a custom error response with a 403 Forbidden status code.


    :param error: error (Exception): The exception to handle. It can be an `HTTPException`
    or any other type of exception.
    Raises:
        HTTPException: Re-raises the input error if it is an instance of `HTTPException`.
        Exception: Raises a custom 403 Forbidden error response with details of the exception.

    Returns:
        NoReturn: This function does not return; it always raises an exception.
    """
    logger.error(f"Exception occurred during user creation: {error}")
    error = error.__dict__
    raise create_error_response(
        status_code=error.get("status_code", http_status.HTTP_403_FORBIDDEN),  # noqa: E501
        title=error.get("title", "Exception occurred"),
        errors={"reason": error.get("reason", "No details available")},
    )
