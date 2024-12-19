import logging

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi import status as http_status
from fastapi.security import HTTPBearer
from starlette.responses import JSONResponse

from app import settings
from app.core.auth_jwt_bearer import JWTBearer
from app.core.exceptions import OptScaleAPIResponseError, handle_exception
from app.invitations.model import (
    DeclineInvitation,
    RegisteredInvitedUserResponse,
    RegisterInvitedUser,
)
from app.invitations.services.external_services import (
    register_invited_user_on_optscale,
    remove_user,
)
from app.optscale_api.auth_api import OptScaleAuth
from app.optscale_api.helpers.auth_tokens_dependency import get_auth_client
from app.optscale_api.invitation_api import OptScaleInvitationAPI
from app.optscale_api.orgs_api import OptScaleOrgAPI
from app.optscale_api.users_api import OptScaleUserAPI

# HTTPBearer scheme to parse Authorization header
bearer_scheme = HTTPBearer()
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    path="/users",
    status_code=http_status.HTTP_201_CREATED,
    response_model=RegisteredInvitedUserResponse,
)
async def register_invited(data: RegisterInvitedUser):
    try:
        response = await register_invited_user_on_optscale(
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


@router.post(
    path="/users/invites/{invite_id}/decline",
    status_code=http_status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(JWTBearer())],
)
async def decline_invitation(
    invite_id: str,
    data: DeclineInvitation,
    background_task: BackgroundTasks,
    invitation_api: OptScaleInvitationAPI = Depends(),
    org_api: OptScaleOrgAPI = Depends(),
    user_api: OptScaleUserAPI = Depends(),
    auth_client: OptScaleAuth = Depends(get_auth_client),
):
    try:
        user_id = data.user_id

        invited_user_token = (
            await auth_client.obtain_user_auth_token_with_admin_api_key(
                admin_api_key=settings.admin_token, user_id=user_id
            )
        )

        response = await invitation_api.decline_invitation(
            user_access_token=invited_user_token, invitation_id=invite_id
        )

        background_task.add_task(
            remove_user,
            user_access_token=invited_user_token,
            user_id=user_id,
            invitation_api=invitation_api,
            org_api=org_api,
            user_api=user_api,
        )
        return JSONResponse(
            status_code=response.get("status_code", http_status.HTTP_200_OK),
            content={"response": "Invitation declined"},
        )
    except OptScaleAPIResponseError as error:
        handle_exception(error=error)
