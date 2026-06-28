from pydantic import BaseModel
from pydantic import EmailStr


class AdminRegister(BaseModel):

    name: str
    email: EmailStr
    password: str


class AdminLogin(BaseModel):

    email: EmailStr
    password: str