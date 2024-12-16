import logging

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import settings
from app.core.api_client import LogRequestMiddleware
from app.router.api_v1.endpoints import api_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
app.add_middleware(LogRequestMiddleware)


if __name__ == "__main__":
    # TODO: get port and host from settings
    uvicorn.run("main:app", port=8080, host="0.0.0.0", reload=True)  # nosec B104
