from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base
    api_v1_prefix: str = "/v1/admin"
    public_url: str
    debug: bool = False
    project_name: str = "CloudSpend API Modifier"
    version: str
    description: str = "Service to provide custom users and org management"
    opt_scale_api_url: str
    secret: str
    algorithm: str = "HS256"
    issuer: str
    audience: str
    default_request_timeout: int = 10  # API Client
    admin_token: str
    # Database
    db_async_connection_str: str
    db_async_test_connection_str: str

    class Config:
        env_file = "/app/.env.test"
