[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=softwareone-platform_ffc-finops-api-modifier&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=softwareone-platform_ffc-finops-api-modifier) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=softwareone-platform_ffc-finops-api-modifier&metric=coverage)](https://sonarcloud.io/summary/new_code?id=softwareone-platform_ffc-finops-api-modifier)

# SoftwareONE OptScale API Modifier

Service that provides custom logic for:

1. Prevent User Self-registration
2. Prevent Creation of Additional Organizations by Organization Admins
3. Prevent Deletion of the Organization by Organization Admins
4. Prevent Creation of Kubernetes, Alibaba Cloud and Databricks datasources
5. Handle the user invitation flow

# Create you .env file

You can use the `env.example` as a bases to setup your running environment and customize it according to your needs.

# Run tests

`docker compose run --rm  app_test`

# Run for Development

`docker compose up app`

# Build production image

To build the production image please use the `prod.Dockefile` dockerfile.

> [!IMPORTANT]
> Developers must take care of keep in sync `dev.Dockerfile` and `prod.Dockerfile`.
