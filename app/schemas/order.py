from pydantic import BaseModel


class OrderCreate(BaseModel):
    address_id: int