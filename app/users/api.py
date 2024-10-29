from __future__ import annotations

import logging
from functools import wraps
from typing import Annotated, Optional, Callable, Any

from fastapi import APIRouter, Depends, status as http_status
from app.core.auth_jwt_bearer import JWTBearer
from app.optscale_api.users_api import OptScaleAPI

logger = logging.getLogger("api.users")
router = APIRouter()


@router.get(
    "",
    status_code=http_status.HTTP_200_OK,
    dependencies=[Depends(JWTBearer())]
)
async def get_sample(

):
    return {"message": "Welcome"}


@router.post(
    path="",
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Depends(JWTBearer())]
)
async def create_user(
        email: str,
        display_name: str,
        password: str
):
    return await OptScaleAPI.create_user(email=email, display_name=display_name, password=password)
