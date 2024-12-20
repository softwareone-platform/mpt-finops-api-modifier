import logging

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi import status as http_status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import JSONResponse

from app import settings
from app.core.exceptions import (
    InvitationDoesNotExist,
    OptScaleAPIResponseError,
    handle_exception,
)
from app.invitations.model import (
    DeclineInvitation,
    RegisteredInvitedUserResponse,
    RegisterInvitedUser,
)
from app.invitations.services.invitations import (
    register_invited_user_on_optscale,
    remove_user,
)
from app.optscale_api.invitation_api import OptScaleInvitationAPI
from app.optscale_api.orgs_api import OptScaleOrgAPI
from app.optscale_api.users_api import OptScaleUserAPI

# HTTPBearer scheme to parse Authorization header
bearer_scheme = HTTPBearer()
logger = logging.getLogger(__name__)
router = APIRouter()


def get_bearer_token(
    auth: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    return auth.credentials  # Return the raw token


def get_optscale_user_api() -> OptScaleUserAPI:
    return OptScaleUserAPI()


@router.post(
    path="/users",
    status_code=http_status.HTTP_201_CREATED,
    response_model=RegisteredInvitedUserResponse,
)
async def register_invited(
    data: RegisterInvitedUser,
    user_api: OptScaleUserAPI = Depends(get_optscale_user_api),
):  # noqa: E501
    try:
        response = await register_invited_user_on_optscale(
            email=str(data.email),
            display_name=data.display_name,
            password=data.password,
            user_api=user_api,
        )
        return JSONResponse(
            status_code=response.get("status_code", http_status.HTTP_201_CREATED),
            content=response.get("data", {}),
        )

    except (OptScaleAPIResponseError, InvitationDoesNotExist) as error:
        handle_exception(error=error)


@router.post(
    path="/users/invites/{invite_id}/decline",
    status_code=http_status.HTTP_200_OK,
)
async def decline_invitation(
    invite_id: str,
    data: DeclineInvitation,
    background_task: BackgroundTasks,
    invitation_api: OptScaleInvitationAPI = Depends(),
    org_api: OptScaleOrgAPI = Depends(),
    user_api: OptScaleUserAPI = Depends(),
    invited_user_token: str = Depends(get_bearer_token),
):
    try:
        user_id = data.user_id
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
            admin_api_key=settings.admin_token,
        )
        return JSONResponse(
            status_code=response.get("status_code", http_status.HTTP_200_OK),
            content={"response": "Invitation declined"},
        )
    except OptScaleAPIResponseError as error:
        handle_exception(error=error)
