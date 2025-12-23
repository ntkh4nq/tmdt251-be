from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.category import Category
from app.schemas.catalog import CategoryCreate, CategoryUpdate
from app.services.utils import commit_to_db


class CategoryService:
    """Service layer for Category operations"""

    @staticmethod
    async def create_category(data: CategoryCreate, db: AsyncSession) -> Category:
        """Create a new category"""
        new_category = Category(**data.model_dump())
        db.add(new_category)
        await commit_to_db(db)
        await db.refresh(new_category)
        return new_category

    @staticmethod
    async def get_categories(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = None
    ) -> List[Category]:
        """Get list of categories with pagination"""
        result = await db.execute(select(Category).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_category_by_id(category_id: int, db: AsyncSession) -> Optional[Category]:
        """Get a category by ID"""
        result = await db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_category_by_name(name: str, db: AsyncSession) -> Optional[Category]:
        """Get a category by name"""
        result = await db.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_category(
        category_id: int,
        data: CategoryUpdate,
        db: AsyncSession
    ) -> Optional[Category]:
        """Update a category"""
        category = await CategoryService.get_category_by_id(category_id, db)
        if not category:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)

        await commit_to_db(db)
        await db.refresh(category)
        return category

    @staticmethod
    async def delete_category(category_id: int, db: AsyncSession) -> bool:
        """Delete a category"""
        category = await CategoryService.get_category_by_id(category_id, db)
        if not category:
            return False

        await db.delete(category)
        await commit_to_db(db)
        return True
