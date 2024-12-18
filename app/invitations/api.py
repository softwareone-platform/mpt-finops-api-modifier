import logging

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi import status as http_status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import JSONResponse

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
from app.optscale_api.invitation_api import OptScaleInvitationAPI

# HTTPBearer scheme to parse Authorization header
bearer_scheme = HTTPBearer()
logger = logging.getLogger(__name__)
router = APIRouter()


def get_bearer_token(
    auth: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    return auth.credentials  # Return the raw token


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
)
async def decline_invitation(
    invite_id: str,
    data: DeclineInvitation,
    background_task: BackgroundTasks,
    invited_user_token: str = Depends(get_bearer_token),
    invitation_api: OptScaleInvitationAPI = Depends(),
):
    try:
        user_id = data.user_id
        response = await invitation_api.decline_invitation(
            user_access_token=invited_user_token, invitation_id=invite_id
        )
        background_task.add_task(
            remove_user, user_access_token=invited_user_token, user_id=user_id
        )
        return JSONResponse(
            status_code=response.get("status_code", http_status.HTTP_204_NO_CONTENT),
            content="",
        )
    except OptScaleAPIResponseError as error:
        handle_exception(error=error)
