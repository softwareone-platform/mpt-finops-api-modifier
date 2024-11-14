from pydantic import BaseModel, EmailStr


class CreateInvitationData(BaseModel):
    email: EmailStr
    display_name: str
    organization_id: str
    model_config = {
        "json_schema_extra" :{
            "example" : [
                {
                   "id" : "1001-10010-1001-1001",
                    "email" : "peter.parker@spiderman.com",
                     "org_id" : "abc-1010-100-10"
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
                    "email" : "peter.parker@spiderman.com",
                    "org_id" : "abc-1010-100-10"
                }
            ]
        }
    }

class CreateInvitationResponse(BaseModel):
    display_name: str
    email: EmailStr
    org_id: str


    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "display_name": "your friendly neighborhood spider-man",
    #             "email": "peter.parker@spider.com",
    #             "org_id": "ABC-1223-ABC-123"
    #             }
    #     }

class CheckInvitationResponse(BaseModel):
    invited: bool
    email: EmailStr


    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "invited": True,
    #             "email": "peter.parker@spider.com"
    #         }
    #     }
