from pydantic import BaseModel, EmailStr


class CreateInvitationData(BaseModel):
    email: EmailStr
    display_name: str
    organization_id: str
    invitation_id : str
    class Config:
        schema_extra = {
            "example":  {
                            "invitation_id" : "1001-10010-1001-1001",
                            "email" : "peter.parker@spiderman.com",
                            "org_id" : "abc-1010-100-10"
                        }
        }

class InvitationResponse(BaseModel):
    id: int
    status: str
    message: str

    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "status": "accepted",
                "message": "Invitation sent successfully."
            }
        }

class CreateInvitationResponse(BaseModel):
    display_name: str
    email: EmailStr
    org_id: str


    class Config:
        schema_extra = {
            "example": {
                "display_name": "your friendly neighborhood spider-man",
                "email": "peter.parker@spider.com",
                "org_id": "ABC-1223-ABC-123"
                }
        }
