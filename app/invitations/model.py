from pydantic import BaseModel, EmailStr


class CreateInvitationData(BaseModel):
    invited_email: EmailStr
    display_name: str
    organization_id: str
    model_config = {
        "json_schema_extra" :{
            "example" : [
                {
                    "invited_email" : "peter.parker@spiderman.com",
                    "display_name" : "Peter Parker",
                    "organization_id" : "abc-1010-100-10",
                }
            ]
        }
    }


class InvitationResponse(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    organization_id: str

    model_config = {
        "json_schema_extra" :{
            "example" : [
                {
                    "id" : "1001-10010-1001-1001",
                    "invited_email" : "peter.parker@spiderman.com",
                    "display_name" : "Peter Parker",
                    "organization_id" : "abc-1010-100-10",
                    "token" : "base64-token",
                    "created_by_user_id": "1010-1001-10010",
                    "created_at" :"2024-11-14:11:10:10",
                    "expiration_date": "2024-11-21:11:10:10"
                }
            ]
        }
    }
