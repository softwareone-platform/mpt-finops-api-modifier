import logging

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from starlette.responses import JSONResponse

from app import settings
from app.core.auth_jwt_bearer import JWTBearer
from app.core.error_formats import create_error_response
from app.core.exceptions import handle_exception
from app.optscale_api.orgs_api import OptScaleOrgAPI
from app.organizations.model import CreateOrgData, OrgDataResponse

logger = logging.getLogger("api.organizations")
router = APIRouter()

@router.get(
    path="",
    status_code=http_status.HTTP_200_OK,
    response_model=OrgDataResponse,
    dependencies=[Depends(JWTBearer())]
)
async def get_orgs(
        user_id: str,
        org_api: OptScaleOrgAPI = Depends()
):
    try:
        response = await org_api.get_user_org(user_id=user_id, admin_api_key=settings.admin_token)
        if response.get("error"):
            logger.error(f"Failed to get the org for the user : {user_id}")
            raise create_error_response(status_code=response.get("status_code",
                                                                 http_status.HTTP_403_FORBIDDEN),
                                        title="Cannot get any organizations",
                                        errors={"reason": response.get("data", {}).
                                        get("error", {}).get("reason", "")})
        return JSONResponse(status_code=response.get("status_code", http_status.HTTP_200_OK),
                            content=response.get("data", {}))

    except Exception as error:
            handle_exception(error)
@router.post(
    path="",
    status_code=http_status.HTTP_201_CREATED,
    response_model=OrgDataResponse,
    dependencies=[Depends(JWTBearer())]
)
async def create_orgs(
        data: CreateOrgData,
        org_api: OptScaleOrgAPI = Depends()
):
    """
    Require Admin Authentication Token

    Create a new FinOps for Cloud organization
    """
    try:
        response = await org_api.create_user_org(org_name=data.org_name,
                                                user_id=data.user_id,
                                                currency=data.currency,
                                                admin_api_key=settings.admin_token)
        if response is None:
            raise create_error_response(status_code=http_status.HTTP_403_FORBIDDEN,
                                        title="Cannot create the Org",
                                        errors={"reason": "An error occurred creating the org"})


        if response.get("error"):
            logger.error(f"Failed to create the org : {data.org_name}")

            raise create_error_response(status_code=response.get("status_code",
                                                                     http_status.HTTP_403_FORBIDDEN),
                                            title="Cannot create the Org",
                                            errors={"reason": response.get("data", {}).
                                            get("error", {}).get("reason", "")})


        return JSONResponse(status_code=response.get("status_code", http_status.HTTP_201_CREATED),
                            content=response.get("data", {}))


    except Exception as error:
        handle_exception(error)
