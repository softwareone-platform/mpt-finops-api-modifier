import logging

from fastapi import APIRouter, Depends, status as http_status, HTTPException
from starlette.responses import JSONResponse

from app.users.model import CreateUserData
from app.core.auth_jwt_bearer import JWTBearer
from app.core.error_formats import create_error_response
from app.optscale_api.users_api import OptScaleUserAPI

logger = logging.getLogger("api.users")
router = APIRouter()


@router.post(
    path="",
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Depends(JWTBearer())]
)
async def create_user(
        data: CreateUserData,
        user_api: OptScaleUserAPI = Depends()
):
    try:
        response = await user_api.create_user(email=data.email,
                                              display_name=data.display_name,
                                              password=data.password)
        if response.get("error"):
            logger.warning(f"Failed to create user with email: {data.email}")
            raise create_error_response(status_code=response.get("status_code", http_status.HTTP_403_FORBIDDEN),
                                        title="Cannot create the user",
                                        errors={"reason": response.get("data", {}).get("error", {}).get("reason", "")})
        return JSONResponse(status_code=response.get("status_code", 200), content=response.get("data", {}))

    except Exception as error:
        logger.error(f"Exception occurred during user creation: {error}")
        raise create_error_response(status_code=http_status.HTTP_403_FORBIDDEN,
                                    title="An exception occurred",
                                    errors={"exception": str(error)})
