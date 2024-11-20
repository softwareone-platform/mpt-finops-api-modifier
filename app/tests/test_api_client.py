import httpx
import pytest
from httpx import Response

from app.core.api_client import APIClient


@pytest.fixture
def mock_base_url():
    return "https://mockapi.com"


@pytest.fixture
def api_client(mock_base_url):
    return APIClient(base_url=mock_base_url, timeout=5)


@pytest.mark.asyncio
async def test_get_successful(api_client, mock_base_url):
    async def mock_response(request: httpx.Request):
        return Response(
            status_code=200,
            json={"message": "success"},
            headers={"Content-Type": "application/json"},
        )

    transport = httpx.MockTransport(mock_response)
    api_client.client._transport = transport

    response = await api_client.get(f"{mock_base_url}/test-endpoint")
    assert response["status_code"] == 200
    assert response["data"] == {"message": "success"}


@pytest.mark.asyncio
async def test_post_successful(api_client, mock_base_url):
    async def mock_response(request: httpx.Request):
        return Response(
            status_code=201,
            json={"id": 1, "name": "Test"},
            headers={"Content-Type": "application/json"},
        )

    transport = httpx.MockTransport(mock_response)
    api_client.client._transport = transport

    response = await api_client.post(f"{mock_base_url}/test-endpoint", data={"name": "Test"})
    assert response["status_code"] == 201
    assert response["data"] == {"id": 1, "name": "Test"}


@pytest.mark.asyncio
async def test_make_request_non_json(api_client):
    async def mock_response(request: httpx.Request):
        return Response(
            status_code=200,
            content=b"Plain text response",
            headers={"Content-Type": "text/plain"},
        )

    transport = httpx.MockTransport(mock_response)
    api_client.client._transport = transport

    response = await api_client.get("/non-json-endpoint")
    assert response["status_code"] == 200
    assert response["error"] == "Plain text response"


@pytest.mark.asyncio
async def test_make_request_invalid_json(api_client):
    async def mock_response(request: httpx.Request):
        return Response(
            status_code=200,
            content=b"This is not valid JSON",
            headers={"Content-Type": "application/json"},
        )

    transport = httpx.MockTransport(mock_response)
    api_client.client._transport = transport

    response = await api_client.get("/invalid-json-endpoint")
    assert response["status_code"] == 200
    assert "Invalid JSON format in response" in response["error"]


@pytest.mark.asyncio
async def test_make_request_connection_error(api_client):
    async def mock_response(request: httpx.Request):
        raise httpx.RequestError("Connection error")

    transport = httpx.MockTransport(mock_response)
    api_client.client._transport = transport

    response = await api_client.get("/connection-error-endpoint")
    assert response["status_code"] == 503
    assert "Connection error" in response["error"]


@pytest.mark.asyncio
async def test_close_client(api_client):
    await api_client.close()
    assert api_client.client.is_closed
