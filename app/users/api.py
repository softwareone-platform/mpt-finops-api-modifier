import logging

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from starlette.responses import JSONResponse

from app.core.auth_jwt_bearer import JWTBearer
from app.core.exceptions import OptScaleAPIResponseError, handle_exception
from app.optscale_api.users_api import OptScaleUserAPI
from app.users.model import CreateUserData, CreateUserResponse

logger = logging.getLogger("api.users")
router = APIRouter()


@router.post(
    path="",
    status_code=http_status.HTTP_201_CREATED,
    response_model=CreateUserResponse,
    dependencies=[Depends(JWTBearer())],
)
async def create_user(data: CreateUserData, user_api: OptScaleUserAPI = Depends()):
    """
    Require Admin Authentication Token

    Create the first FinOps user
    """
    try:
        response = await user_api.create_user(
            email=str(data.email),
            display_name=data.display_name,
            password=data.password,
        )
        return JSONResponse(
            status_code=response.get("status_code", http_status.HTTP_201_CREATED),
            content=response.get("data", {}),
        )

    except OptScaleAPIResponseError as error:
        handle_exception(error=error)
