from pydantic import BaseModel


class CreateOrgData(BaseModel):
    org_name: str
    user_id: str
    currency: str
