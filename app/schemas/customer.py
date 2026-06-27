from pydantic import BaseModel
from pydantic import EmailStr


class CustomerRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str


class CustomerLogin(BaseModel):
    email: EmailStr
    password: str


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str

    class Config:
        from_attributes = True