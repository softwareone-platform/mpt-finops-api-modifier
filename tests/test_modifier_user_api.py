import logging
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.core.exceptions import OptScaleAPIResponseError
from app.optscale_api.users_api import OptScaleUserAPI
from tests.helpers.jwt import create_jwt_token


@pytest.fixture
def mock_create_user():
    patcher = patch.object(OptScaleUserAPI, "create_user", new=AsyncMock())
    mock = patcher.start()
    yield mock
    patcher.stop()


async def test_create_user_no_authentication(
    async_client: AsyncClient, test_data: dict
):
    payload = test_data["user"]["case_create"]["payload"]
    response = await async_client.post("/users", json=payload)
    assert (
        response.status_code == 401
    ), "Expected 401 when no authentication is provided"
    got = response.json()
    assert (
        got.get("detail").get("errors").get("reason") == "Invalid authorization scheme."
    )
    assert "traceId" in got.get("detail")


@pytest.mark.parametrize(
    "token, expected_status",  # noqa: PT006
    [
        (
            "Bearer MDAwZWxvY2F0aW9uIAowMDM0aWRlbnRpZmllciBmMGJkMGM0YS03YzU1LTQ"
            "1YjctOGI1OC0yNzc0MGUzODc4OWEKMDAyMmNpZCBjcmVhdGVkOjE3MzAxMjY1MjEuMDM"
            "wNzU4CjAwMTZjaWQgcmVnaXN0ZXI6VHJ1ZQowMDFhY2lkIHByb3ZpZGVyOm9wdHNjYWxl"
            "CjAwMmZzaWduYXR1cmUg4Ri0H_K4_xmY_fp8WvfIqZbzsrXK0P6I0KVTi8gRHkYK",
            401,
        ),  # Tuple 1
        ("Bearer not_a_jwt_token", 401),  # Tuple 2
    ],
)
async def test_create_user_with_invalid_token(
    token, expected_status, async_client: AsyncClient, test_data: dict
):
    payload = test_data["user"]["case_create"]["payload"]
    response = await async_client.post(
        "/users", json=payload, headers={"Authorization": token}
    )
    assert (
        response.status_code == expected_status
    ), f"Expected {expected_status} for token: {token}"


async def test_create_user_with_valid_authentication(
    async_client: AsyncClient, test_data: dict, mock_create_user
):
    payload = test_data["user"]["case_create"]["payload"]
    jwt_token = create_jwt_token()
    mock_response = test_data["user"]["case_create"]["response"]
    mock_response["data"]["token"] = jwt_token
    # Set return value for the mock `create_user` method
    mock_create_user.return_value = mock_response

    # Send request with valid JWT token
    response = await async_client.post(
        "/users", json=payload, headers={"Authorization": "Bearer " + jwt_token}
    )

    # Verify the response status and JSON structure
    assert response.status_code == 201, "Expected 201 Created for valid user creation"
    got = response.json()
    want = test_data["user"]["case_create"]["response"]["data"]
    want["token"] = jwt_token
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"


async def test_create_user_exception_handling(
    async_client: AsyncClient, test_data: dict, mock_create_user, caplog
):
    # Simulate an exception in `create_user`
    mock_create_user.side_effect = OptScaleAPIResponseError(
        title="Error response from OptScale", reason="Test Exception", status_code=403
    )

    payload = test_data["user"]["case_create"]["payload"]
    jwt_token = create_jwt_token()

    # Capture logs
    with caplog.at_level(logging.ERROR):
        # Send request with valid JWT token
        response = await async_client.post(
            "/users", json=payload, headers={"Authorization": "Bearer " + jwt_token}
        )

    # Verify the response status and content
    assert (
        response.status_code == 403
    ), "Expected 403 Forbidden when an exception occurs in user creation"
    got = response.json()
    assert got.get("detail").get("errors") == {"reason": "Test Exception"}
    # Verify the log entry
    assert (
        "Exception occurred during user creation: Error response from OptScale"
        in caplog.text
    ), "Expected error log message for the exception"
