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


# Run for Development

`docker build -f dev.Dockerfile -t optscale_api_modifier `
`docker run --rm optscale_api_modifier `
