from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base
    api_v1_prefix: str
    debug: bool
    project_name: str
    version: str
    description: str
    opt_scale_api_url: str
    secret: str
    algorithm: str
    issuer: str
    audience: str
    default_request_timeout: int
    admin_token: str
