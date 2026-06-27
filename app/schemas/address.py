from pydantic import BaseModel


class AddressCreate(BaseModel):

    full_name: str
    phone: str
    address_line: str
    city: str
    state: str
    pincode: str
    country: str


class AddressResponse(BaseModel):

    id: int

    full_name: str
    phone: str

    address_line: str

    city: str
    state: str
    pincode: str
    country: str

    is_default: bool

    class Config:
        from_attributes = True