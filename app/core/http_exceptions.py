from typing import Optional

from fastapi import HTTPException
from fastapi import status as http_status


def credential_exception(details: Optional[str] = None):
    if not details:
        details = "Could not validate credentials"
    return HTTPException(
        status_code=http_status.HTTP_401_UNAUTHORIZED,
        detail=details,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden_action(details: Optional[str] = None):
    if not details:
        details = "You are not allowed!"
    return HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail=details)


def duplicate_record(details: Optional[str] = None):
    if not details:
        details = "The item is already stored!"
    return HTTPException(status_code=http_status.HTTP_409_CONFLICT, detail=details)


def not_found_resource(details: Optional[str] = None):
    if not details:
        details = "Sorry, can't find what you searched."
    return HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=details)


def bad_format(details: Optional[str] = None):
    if not details:
        details = (
            "No squealing and remember that it's all in your head. "
            "Check your data format"
        )
    return HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=details)


def unprocessable_entity(details: Optional[str] = None):  # noqa
    if not details:
        details = "Can't process your data"
    return HTTPException(
        status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=details
    )
