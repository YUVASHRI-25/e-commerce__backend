from pydantic import BaseModel


class CartCreate(BaseModel):

    product_id: int
    quantity: int


class CartUpdate(BaseModel):

    quantity: int


class ProductInCart(BaseModel):

    id: int
    name: str
    price: float
    image_url: str | None = None

    class Config:
        from_attributes = True


class CartResponse(BaseModel):

    id: int
    quantity: int
    product: ProductInCart

    class Config:
        from_attributes = True