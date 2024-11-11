import uuid
from typing import Any, Dict, Optional

from fastapi import HTTPException

# Mapping of HTTP status codes to type URLs
STATUS_TYPE_URLS = {
    400: "https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.1",
    401: "https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.3",
    403: "https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.3",
    404: "https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.4",
    405: "https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.5",
    406: "https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.6",
    408: "https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.7",
    409: "https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.8",
    500: "https://datatracker.ietf.org/doc/html/rfc7231#section-6.6.1",
}

DEFAULT_TYPE_URL = "https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.4"


# todo: Add others

def create_error_response(
        status_code: int,
        title: str,
        errors: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Creates a standardized error response.
    Following the guidelines
    https://softwareone.atlassian.net/wiki/spaces/mpt/pages/5020975658/Error+Handling+and+Status+Codes#Standard-Error-Formats-(RFC-7807)

    :param status_code: HTTP status code for the error.
    :param title: A description of the problem.
    :param errors: A dictionary containing error details.
    :return: JSONResponse with the standardized error structure.
    """
    type_url = STATUS_TYPE_URLS.get(status_code, DEFAULT_TYPE_URL)  # 400
    trace_id = uuid.uuid4().hex  # The unique  ID to trace the error
    # todo: check for a specific format for this traceID

    # Validate and serialize the `errors` field
    if errors is not None:
        if not isinstance(errors, dict):
            raise ValueError("`errors` must be a dictionary.")
        errors = {
            key: list(value) if isinstance(value, set) else value
            for key, value in errors.items()
        }

    error_content = {
        "type": type_url,
        "title": title,
        "status": status_code,
        "traceId": trace_id,
        "errors": errors or {},
    }
    # Return the error as an HTTPException
    return HTTPException(status_code=status_code, detail=error_content)
