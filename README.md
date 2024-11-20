[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# SoftwareONE OptScale API Modifier

Service that provides custom logic for:

1. Prevent User Self-registration
2. Prevent Creation of Additional Organizations by Organization Admins
3. Prevent Deletion of the Organization by Organization Admins
4. Prevent Creation of Kubernetes, Alibaba Cloud and Databricks datasources
5. Handle the user invitation flow

# Run tests

`docker build -f test.Dockerfile -t optscale_api_modifier_test .`

`docker run --rm optscale_api_modifier_test  `

or 

`./build_and_run_tests`

# Run for Development

`docker build -f dev.Dockerfile -t optscale_api_modifier .`
`docker run --rm optscale_api_modifier `

# Create you .env file

```
# BASE
API_V1_PREFIX="/v1/admin"
PUBLIC_URL="http://localhost:8000"
DEBUG=True
PROJECT_NAME="CloudSpend API Modifier"
VERSION="0.1.0"
DESCRIPTION="Service to provide custom users and org management"
# CLoudSpend API
OPT_SCALE_API_URL="https://your-optscaledomain.com"
# JWT TOKEN
SECRET="my_super_secret_here"
ALGORITHM=HS256
ISSUER="SWO"
AUDIENCE="modifier"
# API Client
DEFAULT_REQUEST_TIMEOUT=10
# Admin Token
ADMIN_TOKEN="your admin token here"

# DATABASE
DB_ASYNC_CONNECTION_STR="postgresql+asyncpg://postgres:mysecurepass@localhost:5433/your_dev_db_here"
DB_ASYNC_TEST_CONNECTION_STR="postgresql+asyncpg://postgres:mysecurepass@localhost:5434/your_test_db_here"
```
