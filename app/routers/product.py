from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import File

from sqlalchemy.orm import Session
from sqlalchemy import asc
from sqlalchemy import desc

import shutil
from pathlib import Path

from app.database import get_db

from app.models.product import Product
from app.models.category import Category

from app.schemas.product import (
    ProductCreate,
    ProductResponse
)

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):

    category = (
        db.query(Category)
        .filter(
            Category.id == product.category_id
        )
        .first()
    )

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product created successfully",
        "product_id": new_product.id
    }


@router.get(
    "/",
    response_model=list[ProductResponse]
)
def get_products(
    db: Session = Depends(get_db)
):

    return (
        db.query(Product)
        .all()
    )


@router.get("/search/{keyword}")
def search_products(
    keyword: str,
    db: Session = Depends(get_db)
):

    products = (
        db.query(Product)
        .filter(
            Product.name.ilike(
                f"%{keyword}%"
            )
        )
        .all()
    )

    return products

@router.get("/category/{category_id}")
def filter_by_category(
    category_id: int,
    db: Session = Depends(get_db)
):

    products = (
        db.query(Product)
        .filter(
            Product.category_id == category_id
        )
        .all()
    )

    return products

@router.get("/price")
def filter_by_price(
    min_price: float = 0,
    max_price: float = 1000000,
    db: Session = Depends(get_db)
):

    products = (
        db.query(Product)
        .filter(
            Product.price >= min_price,
            Product.price <= max_price
        )
        .all()
    )

    return products

@router.get("/paginated")
def get_products_paginated(
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db)
):

    skip = (page - 1) * limit

    products = (
        db.query(Product)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return products

@router.get("/sort/{field}")
def sort_products(
    field: str,
    db: Session = Depends(get_db)
):

    if field == "price":

        products = (
            db.query(Product)
            .order_by(
                asc(Product.price)
            )
            .all()
        )

    elif field == "-price":

        products = (
            db.query(Product)
            .order_by(
                desc(Product.price)
            )
            .all()
        )

    elif field == "name":

        products = (
            db.query(Product)
            .order_by(
                asc(Product.name)
            )
            .all()
        )

    elif field == "-name":

        products = (
            db.query(Product)
            .order_by(
                desc(Product.name)
            )
            .all()
        )

    else:

        raise HTTPException(
            status_code=400,
            detail="Invalid sort field"
        )

    return products

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = (
        db.query(Product)
        .filter(
            Product.id == product_id
        )
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product

@router.put("/{product_id}")
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db)
):

    existing_product = (
        db.query(Product)
        .filter(
            Product.id == product_id
        )
        .first()
    )

    if existing_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    category = (
        db.query(Category)
        .filter(
            Category.id == product.category_id
        )
        .first()
    )

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.stock = product.stock
    existing_product.category_id = product.category_id

    db.commit()
    db.refresh(existing_product)

    return {
        "message": "Product updated successfully",
        "product": existing_product
    }


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = (
        db.query(Product)
        .filter(
            Product.id == product_id
        )
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if product.image_url:

        BASE_DIR = Path(__file__).resolve().parent.parent.parent

        image_path = (
            BASE_DIR /
            product.image_url.lstrip("/")
        )

        if image_path.exists():
            image_path.unlink()

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }

@router.post("/{product_id}/upload-image")
def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    product = (
        db.query(Product)
        .filter(
            Product.id == product_id
        )
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Project root folder
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # uploads folder
    UPLOAD_DIR = BASE_DIR / "uploads"

    UPLOAD_DIR.mkdir(exist_ok=True)

    # Delete old image if exists
    if product.image_url:

        old_image = (
            BASE_DIR /
            product.image_url.lstrip("/")
        )

        if old_image.exists():
            old_image.unlink()

    filename = f"{product_id}_{file.filename}"

    filepath = (
        UPLOAD_DIR /
        filename
    )

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    product.image_url = f"/uploads/{filename}"

    db.commit()
    db.refresh(product)

    return {
        "message": "Image uploaded successfully",
        "image_url": product.image_url
    }


@router.delete("/{product_id}/delete-image")
def delete_product_image(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = (
        db.query(Product)
        .filter(
            Product.id == product_id
        )
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if not product.image_url:

        raise HTTPException(
            status_code=404,
            detail="No image found"
        )

    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    image_path = (
        BASE_DIR /
        product.image_url.lstrip("/")
    )

    if image_path.exists():
        image_path.unlink()

    product.image_url = None

    db.commit()

    return {
        "message": "Image deleted successfully"
    }

