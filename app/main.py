from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base

from app.models.category import Category
from app.models.customer import Customer
from app.models.address import Address
from app.models.product import Product
from app.models.cart import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.address import router as address_router
from app.routers.category import router as category_router
from app.routers.product import router as product_router
from app.routers.cart import router as cart_router
from app.routers.order import router as order_router
from app.routers.payment import router as payment_router
from app.routers.admin import router as admin_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce Backend"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Upload Folder
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True)

print("BASE_DIR :", BASE_DIR)
print("UPLOAD_DIR :", UPLOAD_DIR)

app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOAD_DIR)),
    name="uploads"
)

# -----------------------------
# Routers
# -----------------------------

app.include_router(auth_router)
app.include_router(address_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(admin_router)