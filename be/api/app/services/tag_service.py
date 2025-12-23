from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.tag import Tag
from app.schemas.catalog import TagCreate
from app.services.utils import commit_to_db


class TagService:
    """Service layer for Tag operations"""

    @staticmethod
    async def create_tag(data: TagCreate, db: AsyncSession) -> Tag:
        """Create a new tag"""
        new_tag = Tag(**data.model_dump())
        db.add(new_tag)
        await commit_to_db(db)
        await db.refresh(new_tag)
        return new_tag

    @staticmethod
    async def get_tags(skip: int = 0, limit: int = 100, db: AsyncSession = None) -> List[Tag]:
        """Get list of tags with pagination"""
        result = await db.execute(select(Tag).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_tag_by_id(tag_id: int, db: AsyncSession) -> Optional[Tag]:
        """Get a tag by ID"""
        result = await db.execute(select(Tag).where(Tag.id == tag_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tag_by_name(name: str, db: AsyncSession) -> Optional[Tag]:
        """Get a tag by name"""
        result = await db.execute(select(Tag).where(Tag.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_tag(tag_id: int, db: AsyncSession) -> bool:
        """Delete a tag"""
        tag = await TagService.get_tag_by_id(tag_id, db)
        if not tag:
            return False

        await db.delete(tag)
        await commit_to_db(db)
        return True
