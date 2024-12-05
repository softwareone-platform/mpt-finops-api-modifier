import json
import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import settings
from app.core.auth_jwt_bearer import JWTBearer
from app.main import app


# Mock dependency to bypass JWTBearer authentication
def mock_jwt_bearer():
    return True  # Mocking successful authentication


def pytest_configure():
    # Override settings with defaults for testing
    settings.Config.env_file = "/app/.env.test"  # to match the container path


# Override JWTBearer dependency for all tests
@pytest.fixture(scope="session", autouse=True)
def override_jwt_bearer():
    app.dependency_overrides[JWTBearer] = mock_jwt_bearer
    yield
    app.dependency_overrides = {}


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url=f"http://{settings.api_v1_prefix}"
    ) as client:
        yield client


@pytest.fixture
def test_data() -> dict:
    path = os.getenv("PYTEST_CURRENT_TEST")
    path = os.path.join(*os.path.split(path)[:-1], "data.json")
    if not os.path.exists(path):
        path = os.path.join("tests/data", "data.json")

    with open(path) as file:
        data = json.loads(file.read())

    return data
