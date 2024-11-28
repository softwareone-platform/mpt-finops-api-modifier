from __future__ import annotations

from pydantic import BaseModel


class CreateOrgData(BaseModel):
    org_name: str
    user_id: str
    currency: str


class OptScaleOrganization(BaseModel):
    id: str
    pool_id: str
    name: str
    created_at: int
    deleted_at: int
    is_demo: bool
    currency: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "64a7424c-0745-4926-bb6d-2125b16c91f9",
                    "pool_id": "f9c65ff7-fa7a-4d91-b2ca-60dcac5422da",
                    "name": "test name",
                    "created_at": 1585680056,
                    "deleted_at": 0,
                    "is_demo": False,
                    "currency": "USD",
                }
            ]
        }
    }


class OptScaleOrganizationResponse(BaseModel):
    organizations: list[OptScaleOrganization] | None = None
