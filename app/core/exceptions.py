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

def handle_exception(error:HTTPException | Exception)-> NoReturn:
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
    if isinstance(error, HTTPException):
        raise error
    else:
        raise create_error_response(status_code=http_status.HTTP_403_FORBIDDEN,
                                    title="An exception occurred",
                                    errors={"exception": str(error)})
