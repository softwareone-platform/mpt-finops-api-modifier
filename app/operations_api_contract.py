import datetime
import uuid
from decimal import Decimal
from enum import Enum
from typing import Annotated, Generic, TypeVar

from fastapi import Depends, FastAPI, status
from fastapi_camelcase import CamelModel
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from pydantic_extra_types.currency_code import Currency

LimitField = Annotated[
    int,
    Field(gt=0, le=100, default=100, description="Number of records to return"),
]

OffsetField = Annotated[
    int,
    Field(ge=0, default=0, description="Number of records to skip"),
]


T = TypeVar("T")


class PaginationParams(BaseModel):
    limit: LimitField
    offset: OffsetField


class PaginationData(BaseModel):
    limit: LimitField
    offset: OffsetField
    total: Annotated[int, Field(description="Total number of records available", ge=0)]


class PaginatedResponse(BaseModel, Generic[T]):
    pagination: PaginationData
    items: list[T] = Field(description="List of items for the current page")


class DataSourceType(str, Enum):
    AWS_ROOT = "aws_root"
    AWS_LINKED = "aws_linked"
    AZURE_TENANT = "azure_tenant"
    AZURE_SUBSCRIPTION = "azure_subscription"
    GCP = "gcp"


class UserRole(str, Enum):
    ORGANISATION_MANAGER = "organisation_manager"
    MANAGER = "manager"
    ENGINEER = "engineer"


# Organization Models
class OrganizationBase(CamelModel):
    name: str = Field(
        description="The name of the organization",
        examples=["Apple Inc."],
    )
    currency: Currency = Field(
        description="The primary currency used by the organization for financial operations",
        examples=["USD"],
    )


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: uuid.UUID
    limit: Decimal = Field(
        description="Maximum spending limit set for the organization",
        examples=["50000.00"],
    )
    expenses_last_month: Decimal = Field(
        description="Total expenses from the previous month",
        examples=["42350.75"],
    )
    expenses_this_month: Decimal = Field(
        description="Current month's accumulated expenses",
        examples=["23150.25"],
    )
    expenses_month_forecast: Decimal = Field(
        description="Predicted total expenses for the current month",
        examples=["45000.00"],
    )
    possible_monthly_savings: Decimal = Field(
        description="Estimated amount that could be saved based on current spending patterns",
        examples=["5000.00"],
    )

    class Config:
        from_attributes = True


# User Models
class UserBase(CamelModel):
    email: EmailStr


class UserCreate(UserBase):
    organisation_id: uuid.UUID
    role: UserRole


class UserUpdate(UserBase):
    pass


class User(UserBase):
    id: uuid.UUID
    organisation_id: uuid.UUID
    role: UserRole
    created_at: datetime.datetime
    last_login_at: datetime.datetime

    class Config:
        from_attributes = True


# Entitlement Models
class EntitlementBase(CamelModel):
    sponsor_name: str = Field(
        description="Name of the sponsor for this entitlement", examples=["AWS"]
    )
    sponsor_external_id: str = Field(
        description="Vendor account number from MPT", examples=["ACC-1234-5678"]
    )
    sponsor_container_id: str = Field(
        description="Azure Sub ID, AWS Account number, GCP Project ID etc.",
        examples=["d4500e78-ac78-4445-89e8-5b8a4d482035"],
    )


class EntitlementCreate(EntitlementBase):
    pass


class EntitlementUpdate(EntitlementBase):
    pass


class DataSource(CamelModel):
    organisation_id: uuid.UUID = Field(
        description="ID of the organization this data source belongs to",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    type: DataSourceType = Field(
        description="Type of the data source", examples=["aws_root"]
    )
    resources_changed_this_month: int = Field(
        description="Number of resources that changed during the current month",
        examples=[42],
    )
    expenses_so_far_this_month: Decimal = Field(
        description="Current month's expenses up to now", examples=["1234.56"]
    )
    expenses_forecast_this_month: Decimal = Field(
        description="Forecasted expenses for the current month", examples=["2500.00"]
    )
    icon_url: HttpUrl = Field(
        description="URL to the icon representing this data source",
        examples=["https://example.com/icons/aws.png"],
    )

    class Config:
        from_attributes = True


class Entitlement(EntitlementBase):
    entitlement_id: uuid.UUID = Field(
        description="Unique identifier for the entitlement",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    activated_at: datetime.datetime | None = Field(
        description="Timestamp when the entitlement was activated",
    )
    activated_by: uuid.UUID | None = Field(
        description="User ID who activated the entitlement",
    )
    terminated_at: datetime.datetime | None = Field(
        description="Timestamp when the entitlement was terminated",
        examples=["2023-12-31T12:00:00Z"],
    )
    terminated_by: uuid.UUID | None = Field(
        description="User ID who terminated the entitlement",
    )

    class Config:
        from_attributes = True


app = FastAPI(
    title="Optscale Operations API",
    description="API to be used by Operators to manage Optscale",
)

tags_metadata = [
    {
        "name": "Organizations",
        "description": "Operations with organizations",
    },
    {
        "name": "Users",
        "description": "Operations with users",
    },
    {
        "name": "Entitlements",
        "description": "Operations with entitlements",
    },
    {
        "name": "Data Sources",
        "description": "Read-only operations with data sources",
    },
]

app = FastAPI(openapi_tags=tags_metadata)


# Organization endpoints
@app.post(
    "/v1/organizations/",
    response_model=Organization,
    status_code=status.HTTP_201_CREATED,
    tags=["Organizations"],
)
async def create_organization(organization: OrganizationCreate):
    pass


@app.get(
    "/v1/organizations/",
    response_model=PaginatedResponse[Organization],
    tags=["Organizations"],
)
async def list_organizations(pagination: PaginationParams = Depends()):
    pass


@app.get(
    "/v1/organizations/{organization_id}",
    response_model=Organization,
    tags=["Organizations"],
)
async def get_organization(organization_id: uuid.UUID):
    pass


@app.put(
    "/v1/organizations/{organization_id}",
    response_model=Organization,
    tags=["Organizations"],
)
async def update_organization(
    organization_id: uuid.UUID, organization: OrganizationUpdate
):
    pass


# User endpoints
@app.post(
    "/v1/users/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
async def create_user(user: UserCreate):
    pass


@app.get("/v1/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: uuid.UUID):
    pass


@app.put("/v1/users/{user_id}", response_model=User, tags=["Users"])
async def update_user(user_id: uuid.UUID, user: UserUpdate):
    pass


@app.get(
    "/v1/organizations/{organization_id}/users/",
    response_model=PaginatedResponse[User],
    tags=["Users"],
)
async def list_organization_users(
    organization_id: uuid.UUID, pagination: PaginationParams = Depends()
):
    pass


# Entitlement endpoints
@app.post(
    "/v1/entitlements/",
    response_model=Entitlement,
    status_code=status.HTTP_201_CREATED,
    tags=["Entitlements"],
)
async def create_entitlement(entitlement: EntitlementCreate):
    pass


@app.get(
    "/v1/entitlements/",
    response_model=PaginatedResponse[Entitlement],
    tags=["Entitlements"],
)
async def list_entitlements(pagination: PaginationParams = Depends()):
    pass


@app.get(
    "/v1/entitlements/{entitlement_id}",
    response_model=Entitlement,
    tags=["Entitlements"],
)
async def get_entitlement(entitlement_id: uuid.UUID):
    pass


@app.put(
    "/v1/entitlements/{entitlement_id}",
    response_model=Entitlement,
    tags=["Entitlements"],
)
async def update_entitlement(entitlement_id: uuid.UUID, entitlement: EntitlementUpdate):
    pass


@app.post(
    "/v1/entitlements/{entitlement_id}/terminate",
    response_model=Entitlement,
    tags=["Entitlements"],
)
async def terminate_entitlement(entitlement_id: uuid.UUID):
    pass


# Data Source endpoints
@app.get(
    "/v1/data-sources/",
    response_model=PaginatedResponse[DataSource],
    tags=["Data Sources"],
)
async def list_data_sources(pagination: PaginationParams = Depends()):
    pass


@app.get(
    "/v1/data-sources/{data_source_id}",
    response_model=DataSource,
    tags=["Data Sources"],
)
async def get_data_source(data_source_id: uuid.UUID):
    pass


@app.get(
    "/v1/organizations/{organization_id}/data-sources/",
    response_model=PaginatedResponse[DataSource],
    tags=["Data Sources"],
)
async def list_organization_data_sources(
    organization_id: uuid.UUID, pagination: PaginationParams = Depends()
):
    pass
