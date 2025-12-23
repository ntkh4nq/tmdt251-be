from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_db
from app.schemas.catalog import CategoryCreate, CategoryUpdate, CategoryOut
from app.services.category_service import CategoryService

router = APIRouter(prefix="/catalog/categories", tags=["Categories"])


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new category"""
    # Check if category name already exists
    existing = await CategoryService.get_category_by_name(data.name, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{data.name}' already exists"
        )
    
    return await CategoryService.create_category(data, db)


@router.get("", response_model=List[CategoryOut])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get list of categories with pagination"""
    if limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit cannot exceed 100"
        )
    return await CategoryService.get_categories(skip, limit, db)


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a category by ID"""
    category = await CategoryService.get_category_by_id(category_id, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    return category


@router.put("/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a category"""
    # Check if new name conflicts with existing
    if data.name:
        existing = await CategoryService.get_category_by_name(data.name, db)
        if existing and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{data.name}' already exists"
            )
    
    category = await CategoryService.update_category(category_id, data, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a category"""
    success = await CategoryService.delete_category(category_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    return None
