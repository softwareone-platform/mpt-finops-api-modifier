from __future__ import annotations

import logging
from typing import NoReturn

from fastapi import status as http_status

from app.core.error_formats import create_error_response

logger = logging.getLogger(__name__)


class UserCreationError(Exception):
    """Custom exception for errors during user creation."""

    pass


class UserAccessTokenError(Exception):
    """Custom exception for errors during user access token creation."""

    pass


class UserOrgCreationError(Exception):
    """Custom exception for errors during organization creation."""

    pass


class OptScaleAPIResponseError(Exception):
    """
    Custom exception class for handling errors in the OptScale API responses.

    Attributes:
        status_code (int): The HTTP status code of the API response.
        title (str): A short title describing the error.
        reason (str): A detailed reason explaining the cause of the error.
    """

    def __init__(self, status_code: int, title: str, reason: str):
        """
        Initializes the exception with the given status code, title, and reason.

        :param status_code: The HTTP status code of the API response.
        :param title: A short title describing the error.
        :param reason: A detailed reason explaining the cause of the error.
        """
        message = f"{title}"
        super().__init__(message)
        self.status_code = status_code
        self.title = title
        self.reason = reason


def handle_exception(error: Exception) -> NoReturn:
    """
    Handles exceptions during user creation by logging the error and raising an
    appropriate HTTP response.

    :param error: error (Exception): The exception to handle.
    Raises:
        Exception: Raises a HTTPException exception with custom details of the exception.

    Returns:
        NoReturn: This function does not return; it always raises an exception.
    """
    logger.error(f"Exception occurred during user creation: {error}")
    error = error.__dict__
    raise create_error_response(
        status_code=error.get("status_code", http_status.HTTP_403_FORBIDDEN),
        title=error.get("title", "Exception occurred"),
        errors={"reason": error.get("reason", "No details available")},
    )
