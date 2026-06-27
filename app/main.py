from fastapi import FastAPI
from app.models.category import Category
from app.database import engine, Base
from app.routers.category import router as category_router
from app.models.customer import Customer
from app.models.address import Address
from app.models.product import Product
from app.models.cart import CartItem
from app.routers.auth import router as auth_router
from app.routers.address import router as address_router
from app.routers.product import router as product_router
from app.routers.cart import router as cart_router
from app.models.order import Order
from app.models.order_item import OrderItem
from app.routers.order import router as order_router
from app.models.payment import Payment
from app.routers.payment import router as payment_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce Backend"
)

app.include_router(auth_router)
app.include_router(address_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(payment_router)
