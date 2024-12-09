from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base
    public_url: str
    version: str
    secret: str
    issuer: str
    audience: str
    opt_scale_api_url: str
    admin_token: str
    api_v1_prefix: str = "/v1/admin"
    debug: bool = False
    project_name: str = "CloudSpend API Modifier"
    description: str = "Service to provide custom users and org management"
    algorithm: str = "HS256"
    leeway: float = 30.0
    default_request_timeout: int = 10  # API Client

    class Config:
        env_file = "/app/.env.test"
