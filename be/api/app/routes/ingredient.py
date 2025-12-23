from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_db
from app.schemas.catalog import IngredientCreate, IngredientOut
from app.services.ingredient_service import IngredientService

router = APIRouter(prefix="/catalog/ingredients", tags=["Ingredients"])


@router.post("", response_model=IngredientOut, status_code=status.HTTP_201_CREATED)
async def create_ingredient(
    data: IngredientCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new ingredient"""
    # Check if ingredient name already exists
    existing = await IngredientService.get_ingredient_by_name(data.name, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with name '{data.name}' already exists"
        )
    
    return await IngredientService.create_ingredient(data, db)


@router.get("", response_model=List[IngredientOut])
async def get_ingredients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get list of ingredients with pagination"""
    return await IngredientService.get_ingredients(skip, limit, db)


@router.get("/{ingredient_id}", response_model=IngredientOut)
async def get_ingredient(
    ingredient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get an ingredient by ID"""
    ingredient = await IngredientService.get_ingredient_by_id(ingredient_id, db)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {ingredient_id} not found"
        )
    return ingredient


@router.patch("/{ingredient_id}/stock")
async def update_ingredient_stock(
    ingredient_id: int,
    quantity: float = Query(..., ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Update ingredient stock quantity"""
    ingredient = await IngredientService.update_ingredient_stock(ingredient_id, quantity, db)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {ingredient_id} not found"
        )
    return {"message": "Ingredient stock updated successfully", "stock_quantity": ingredient.stock_quantity}


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(
    ingredient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an ingredient"""
    success = await IngredientService.delete_ingredient(ingredient_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {ingredient_id} not found"
        )
    return None
