from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.ingredient import Ingredient
from app.schemas.catalog import IngredientCreate
from app.services.utils import commit_to_db


class IngredientService:
    """Service layer for Ingredient operations"""

    @staticmethod
    async def create_ingredient(data: IngredientCreate, db: AsyncSession) -> Ingredient:
        """Create a new ingredient"""
        new_ingredient = Ingredient(**data.model_dump())
        db.add(new_ingredient)
        await commit_to_db(db)
        await db.refresh(new_ingredient)
        return new_ingredient

    @staticmethod
    async def get_ingredients(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = None
    ) -> List[Ingredient]:
        """Get list of ingredients with pagination"""
        result = await db.execute(select(Ingredient).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_ingredient_by_id(ingredient_id: int, db: AsyncSession) -> Optional[Ingredient]:
        """Get an ingredient by ID"""
        result = await db.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_ingredient_by_name(name: str, db: AsyncSession) -> Optional[Ingredient]:
        """Get an ingredient by name"""
        result = await db.execute(select(Ingredient).where(Ingredient.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_ingredient_stock(
        ingredient_id: int,
        quantity: float,
        db: AsyncSession
    ) -> Optional[Ingredient]:
        """Update ingredient stock quantity"""
        ingredient = await IngredientService.get_ingredient_by_id(ingredient_id, db)
        if not ingredient:
            return None

        ingredient.stock_quantity = quantity
        await commit_to_db(db)
        await db.refresh(ingredient)
        return ingredient

    @staticmethod
    async def delete_ingredient(ingredient_id: int, db: AsyncSession) -> bool:
        """Delete an ingredient"""
        ingredient = await IngredientService.get_ingredient_by_id(ingredient_id, db)
        if not ingredient:
            return False

        await db.delete(ingredient)
        await commit_to_db(db)
        return True
