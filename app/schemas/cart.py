from pydantic import BaseModel


class CartCreate(BaseModel):

    product_id: int
    quantity: int


class CartUpdate(BaseModel):

    quantity: int