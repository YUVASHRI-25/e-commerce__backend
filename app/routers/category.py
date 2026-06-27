from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.category import Category

from app.schemas.category import (
    CategoryCreate,
    CategoryResponse
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/")
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):

    existing_category = (
        db.query(Category)
        .filter(
            Category.name == category.name
        )
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    new_category = Category(
        name=category.name,
        description=category.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return {
        "message": "Category created successfully",
        "category_id": new_category.id
    }

@router.get(
    "/",
    response_model=list[CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db)
):

    categories = (
        db.query(Category)
        .all()
    )

    return categories

@router.get(
    "/",
    response_model=list[CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db)
):

    categories = (
        db.query(Category)
        .all()
    )

    return categories

@router.put("/{category_id}")
def update_category(
    category_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db)
):

    existing_category = (
        db.query(Category)
        .filter(
            Category.id == category_id
        )
        .first()
    )

    if not existing_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    existing_category.name = category.name
    existing_category.description = (
        category.description
    )

    db.commit()
    db.refresh(existing_category)

    return {
        "message":
        "Category updated successfully"
    }

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):

    category = (
        db.query(Category)
        .filter(
            Category.id == category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()

    return {
        "message":
        "Category deleted successfully"
    }


