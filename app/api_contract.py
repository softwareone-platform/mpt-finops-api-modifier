import datetime
import enum
import uuid
from typing import Annotated

from fastapi import FastAPI, Header, status
from pydantic import BaseModel, EmailStr, Field, JsonValue

app = FastAPI()


JWTToken = Annotated[
    str,
    Header(
        alias="Authroization",
        title="JWT Token",
        description="The JWT token used for authorization in `Bearer <token>` format",
    ),
]

CloudUserToken = Annotated[
    str,
    Header(
        alias="Authroization",
        title="FinOps for Cloud user token",
        description="The token used for authorization in `Bearer <token>` format",
    ),
]


class ErrorResponse(BaseModel):
    detail: str


class CommonPrivateFields:
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: Annotated[
        datetime.datetime | None,
        Field(
            default=None,
            examples=[None],
            description="If not null, the timestamp the object was deleted at",
        ),
    ]


class CreateOrgRequest(BaseModel):
    display_name: Annotated[str, Field(examples=["Apple Inc."])]


class OrganizationDetail(BaseModel, CommonPrivateFields):
    display_name: Annotated[str, Field(examples=["Apple Inc."])]
    external_id: Annotated[
        str,
        Field(
            description="the ID of the account of the MPT platform which owns this organization"
        ),
    ]
    cloudspend_id: uuid.UUID


class CreateUserRequest(BaseModel):
    email: EmailStr
    organization_id: uuid.UUID
    display_name: Annotated[str, Field(examples=["Tim Cook"])]


class UserDetail(BaseModel, CommonPrivateFields):
    email: EmailStr
    organization_id: uuid.UUID
    display_name: Annotated[str, Field(examples=["Tim Cook"])]
    cloudspend_id: uuid.UUID


class CloudType(enum.Enum):
    AWS_ROOT = "aws_root"
    AWS_LINKED = "aws_linked"
    AZURE_TENANT = "azure_tenant"
    AZURE_SUBSCRIPTION = "azure_subscription"
    GCP = "gcp"
    ALIBABA = "alibaba"
    DATABRICKS = "databricks"
    KUBERNETES = "kubernetes"


class AWSExportType(enum.Enum):
    STANDARD_DATA_EXPORT = "standard_data_export"
    LEGACY_COST_AND_USAGE = "legacy_cost_and_usage"


class AWSExportConfig(BaseModel):
    create_new_data_export: Annotated[
        bool,
        Field(
            default=True,
            description=(
                "If set to True, a new data export will be created, "
                "otherwise only connect to data in bucket"
            ),
        ),
    ]
    export_name: str
    export_s3_bucket_name: str
    export_path_prefix: str


class AWSRootAccountConfig(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    use_aws_edp: Annotated[
        bool, Field(default=False, description="Use AWS Enterprise Discount Program?")
    ]
    export_type: Annotated[
        AWSExportType, Field(default=AWSExportType.STANDARD_DATA_EXPORT)
    ]
    export_config: Annotated[
        AWSExportConfig | None,
        Field(
            default=None,
            description=(
                "If set to None, the existing data exports will be automatically detected, "
                "otherwise use these fields to manually configure the export"
            ),
        ),
    ]


class AWSLinkedAccountConfig(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str


class AzureTenantAccountConfig(BaseModel):
    directory_tenant_id: str
    application_client_id: str
    secret: str


class AzureSubscriptionAccountConfig(BaseModel):
    directory_tenant_id: str
    application_client_id: str
    secret: str
    subscription_id: str


class GCPAccountConfig(BaseModel):
    credentials_json: JsonValue
    billing_data_dataset_name: str
    billing_data_table_name: str
    billing_dataset_project_id: str | None


class AlibabaAccountConfig(BaseModel):
    cloud_access_key_id: str
    cloud_secret_access_key: str


class DatabricksAccountConfig(BaseModel):
    account_id: str
    client_id: str
    client_secret: str


class KubernetesAccountConfig(BaseModel):
    username: str
    password: str | None


CloudAccountConfig = (
    AWSRootAccountConfig
    | AWSLinkedAccountConfig
    | AzureTenantAccountConfig
    | AzureSubscriptionAccountConfig
    | GCPAccountConfig
    | AlibabaAccountConfig
    | DatabricksAccountConfig
    | KubernetesAccountConfig
)


class CreateDatasourceRequest(BaseModel):
    name: Annotated[
        str, Field(description="Name of the datasource", examples=["Main AWS account"])
    ]
    cloud_type: CloudType
    account_config: Annotated[
        CloudAccountConfig,
        Field(
            description=(
                "Object with credentials to access the cloud account, "
                "the format is dependant on the cloud_type value"
            ),
        ),
    ]


class DatasourceDetail(BaseModel, CommonPrivateFields):
    name: Annotated[
        str, Field(description="Name of the datasource", examples=["Main AWS account"])
    ]
    cloud_type: CloudType
    cloudspend_id: uuid.UUID


class InvitationDetail(BaseModel):
    invited_user_email: EmailStr
    invited_by_user_id: uuid.UUID
    invited_at: datetime.datetime


class InviteUserRequest(BaseModel):
    invited_user_email: EmailStr
    organization_id: uuid.UUID


@app.post(
    "/v1/admin/organizations",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Invalid JWT token",
        }
    },
)
async def create_organization(  # type: ignore
    jwt_token: JWTToken,
    org_data: CreateOrgRequest,
) -> OrganizationDetail:
    """
    Create a new FinOps for Cloud organization (empty)
    """


@app.get(
    "/v1/admin/organizations",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Invalid user token",
        },
    },
)
async def list_organizations(user: CloudUserToken) -> list[OrganizationDetail]:  # type: ignore
    """Lists all the organizations a user is member of"""


@app.post(
    "/v1/admin/users",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": (
                "The JWT token is not present in the request "
                "and the user hasn't been invited to any organization"
            ),
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "The user hasn't been invited to the organization",
        },
        status.HTTP_410_GONE: {
            "model": ErrorResponse,
            "description": "The user didn't accept the invitation before it expired",
        },
    },
)
async def create_user(  # type: ignore
    jwt_token: JWTToken | None,
    user_data: CreateUserRequest,
) -> UserDetail:
    """
    Create a new user for a given organization.

    To create an organization manager user, JWT token-based authentication is required.

    All other user roles must not provide a JWT token but they need to have already accepted
    an invitation (using the `/v1/admin/invitations/accept` endpoint, a link to which is
    included in the invitation email they receive once the organization manager has invited them)
    """


@app.post(
    "/v1/admin/datasources",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Unsupported cloud type (alibaba, k8s, databricks)",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Invalid user token",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "The user is not the organization manager",
        },
    },
)
async def create_datasource(  # type: ignore
    user: CloudUserToken,
    datasource_data: CreateDatasourceRequest,
) -> DatasourceDetail:
    """Create a new FinOps for Cloud datasource"""


@app.get("/v1/admin/datasources")
async def list_datasources(user: CloudUserToken) -> list[DatasourceDetail]:  # type: ignore
    """Lists all the datasources configured for an organization"""


@app.get(
    "/v1/admin/invitations",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Invalid user token",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "The user is not the organization manager",
        },
    },
)
async def list_invitations(  # type: ignore
    user: CloudUserToken,
    organization_id: uuid.UUID,
) -> list[InvitationDetail]:
    """
    List invitations sent out to users within the organization
    """


@app.post(
    "/v1/admin/invitations",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Invalid user token",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "The user is not the organization manager",
        },
    },
)
async def invite_user(
    user: CloudUserToken,
    invitation_data: InviteUserRequest,
):
    """
    Invites a new user to a given organization (sends an invitation email)

    Can only be called by the organization manager user
    """


@app.get(
    "/v1/admin/invitations/accept",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Invalid invitation token",
        },
        status.HTTP_410_GONE: {
            "model": ErrorResponse,
            "description": "The invitation has expired",
        },
    },
)
async def accept_invitation(invitation_token: str):
    """
    Accepts an invitation from an organization manager and allows the user to register
    (if they haven't done so already, e.g. for a different organization)

    NOTE: The HTTP method of this endpoint is intentionally GET instead of POST.
          This is because when a user gets invited, they will recieve an email with
          a link to this endpoint with the invitation token already populated and
          clicking on that link will result in a GET request.
    """
