import logging

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from starlette.responses import JSONResponse

from app.core.auth_jwt_bearer import JWTBearer
from app.datasources.model import CreateDatasource, DatasourceResponse
from app.optscale_api.orgs_api import OptScaleOrgAPI

logger = logging.getLogger("api.organizations")
router = APIRouter()


@router.post(
    path="",
    status_code=http_status.HTTP_201_CREATED,
    response_model=DatasourceResponse,
    dependencies=[Depends(JWTBearer())]
)
async def create_datasource(
        data: CreateDatasource,
        org_api: OptScaleOrgAPI = Depends()
):
    """
    Require user authentication token

    Create a Datasource Cloud Account
    """
    return JSONResponse(status_code=201,
                        content={})
