import logging
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.core.exceptions import OptScaleAPIResponseError, UserAccessTokenError
from app.optscale_api.orgs_api import OptScaleOrgAPI
from tests.helpers.jwt import create_jwt_token


@pytest.fixture
def mock_get_org():
    patcher = patch.object(
        OptScaleOrgAPI, "access_user_org_list_with_admin_key", new=AsyncMock()
    )
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture
def mock_create_org():
    patcher = patch.object(OptScaleOrgAPI, "create_user_org", new=AsyncMock())
    mock = patcher.start()
    yield mock
    patcher.stop()


async def test_create_org_no_authentication(async_client: AsyncClient, test_data: dict):
    payload = test_data["org"]["case_create"]["payload"]
    # Send request without authentication header
    response = await async_client.post("/organizations", json=payload)
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
        ),
        ("Bearer not_a_jwt_token", 401),
    ],
)
async def test_create_org_with_invalid_token(
    async_client: AsyncClient, test_data: dict, token, expected_status
):
    payload = test_data["org"]["case_create"]["payload"]
    # Send request with invalid JWT token
    response = await async_client.post(
        "/organizations", json=payload, headers={"Authorization": token}
    )
    assert (
        response.status_code == expected_status
    ), f"Expected {expected_status} for token: {token}"


async def test_create_org_with_valid_token(
    async_client: AsyncClient, test_data: dict, mock_create_org
):
    payload = test_data["org"]["case_create"]["payload"]
    jwt_token = create_jwt_token()
    mock_response = test_data["org"]["case_create"]["response"]
    # set return value for the mock `create_org` method
    mock_create_org.return_value = mock_response

    # Send request with valid JWT token
    response = await async_client.post(
        "/organizations", json=payload, headers={"Authorization": "Bearer " + jwt_token}
    )
    # Verify the response status and JSON structure
    assert response.status_code == 201, "Expected 201 Created for valid org creation"
    got = response.json()
    want = test_data["org"]["case_create"]["response"]["data"]
    for k, v in want.items():
        assert (
            got[k] == v
        ), f"Mismatch in response for key '{k}': expected {v}, got {got[k]}"


async def test_create_org_exception_handling(
    async_client: AsyncClient, test_data: dict, mock_create_org, caplog
):
    # Simulate an exception in create_user_org
    mock_create_org.side_effect = Exception("Test exception")

    payload = test_data["org"]["case_create"]["payload"]
    jwt_token = create_jwt_token()

    # Capture logs
    with caplog.at_level(logging.ERROR):
        # Send request with valid JWT token
        response = await async_client.post(
            "/organizations",
            json=payload,
            headers={"Authorization": "Bearer " + jwt_token},
        )

    # Verify the response status and content
    assert (
        response.status_code == 403
    ), "Expected 403 Forbidden when an exception occurs in user creation"
    got = response.json()
    assert got.get("detail").get("errors") == {"reason": "No details available"}
    # Verify the log entry
    assert (
        "Exception occurred during user creation: Test exception" in caplog.text
    ), "Expected error log message for the exception"


async def test_get_org_no_authentication(async_client: AsyncClient, test_data: dict):
    response = await async_client.get("/organizations")
    assert (
        response.status_code == 401
    ), "Expected 401 when no authentication is provided"
    got = response.json()
    assert (
        got.get("detail").get("errors").get("reason") == "Invalid authorization scheme."
    )
    assert "traceId" in got.get("detail")


async def test_get_orgs_valid_response(
    async_client: AsyncClient, mock_get_org, test_data: dict
):
    jwt_token = create_jwt_token()
    mocked_response = test_data["org"]["case_get"]["response"]
    mock_get_org.return_value = mocked_response
    response = await async_client.get(
        "/organizations?user_id=101010011",
        headers={"Authorization": f"Bearer {jwt_token}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status, expected_title, expected_reason",  # noqa: PT006
    [
        (
            OptScaleAPIResponseError(
                title="Error response from OptScale",
                reason="test reason",
                status_code=403,
            ),
            403,
            "Error response from OptScale",
            "test reason",
        ),
        (
            UserAccessTokenError("Access Token User ID mismatch"),
            403,
            "Exception occurred",
            "No details available",
        ),
        (
            Exception("generic exception"),
            403,
            "Exception occurred",
            "No details available",
        ),
    ],
)
async def test_get_orgs_exception_handling(
    async_client: AsyncClient,
    mock_get_org,
    exception,
    expected_status,
    expected_title,
    expected_reason,
):
    jwt_token = create_jwt_token()
    mock_get_org.side_effect = exception

    response = await async_client.get(
        "/organizations?user_id=101010011",
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    response_json = response.json()

    assert response.status_code == expected_status
    assert response_json.get("detail").get("title") == expected_title
    assert response_json.get("detail").get("errors").get("reason") == expected_reason
