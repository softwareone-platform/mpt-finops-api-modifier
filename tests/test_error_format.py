import pytest
from fastapi import HTTPException

from app.core.error_formats import (
    DEFAULT_TYPE_URL,
    STATUS_TYPE_URLS,
    create_error_response,
)


@pytest.mark.parametrize("status_code, title, errors, expected_type", [
    (400, "Validation Error", {"field": ["Invalid value"]}, STATUS_TYPE_URLS[400]),
    (401, "Unauthorized", None, STATUS_TYPE_URLS[401]),
    (403, "Forbidden", {"resource": ["Access denied"]}, STATUS_TYPE_URLS[403]),
    (404, "Resource Not Found", {"id": ["Not found"]}, STATUS_TYPE_URLS[404]),
    (426, "Upgrade Required", {"reason": "upgrade required"}, DEFAULT_TYPE_URL),  # Default type
])
def test_create_error_response_valid(status_code, title, errors, expected_type):
    """Test valid inputs for create_error_response."""
    response = create_error_response(status_code, title, errors)
    detail = response.detail

    # Check general structure
    assert isinstance(response, HTTPException)
    assert response.status_code == status_code

    # Validate detail content
    assert detail["type"] == expected_type
    assert detail["title"] == title
    assert detail["status"] == status_code
    assert "traceId" in detail and isinstance(detail["traceId"], str)
    assert detail["errors"] == (errors or {})


def test_create_error_response_invalid_errors():
    """Test when `errors` is not a dictionary."""
    with pytest.raises(ValueError, match="`errors` must be a dictionary."):
        create_error_response(
            status_code=400,
            title="Validation Error",
            errors=["This is invalid"]  # Invalid type
        )


def test_create_error_response_default_type_url():
    """Test that the default type URL is used for unknown status codes."""
    response = create_error_response(
        status_code=123,
        title="Unknown Error",
        errors={"reason": ["Somebody ate the cake!"]}
    )
    detail = response.detail

    # Check default type URL
    assert detail["type"] == DEFAULT_TYPE_URL
    assert detail["title"] == "Unknown Error"
    assert detail["status"] == 123
    assert detail["errors"]["reason"] == ["Somebody ate the cake!"]
