from pydantic import BaseModel, EmailStr, constr


class CreateUserData(BaseModel):
    email: EmailStr
    display_name: str
    password: constr(min_length=8)
