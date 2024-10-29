from os import getenv

from dotenv import load_dotenv

import app.core.logging_config
from app.core.config import Settings

load_dotenv(getenv("ENV_FILE"))

settings = Settings()
