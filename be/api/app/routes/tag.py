from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_db
from app.schemas.catalog import TagCreate, TagOut
from app.services.tag_service import TagService

router = APIRouter(prefix="/catalog/tags", tags=["Tags"])


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new tag"""
    # Check if tag name already exists
    existing = await TagService.get_tag_by_name(data.name, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{data.name}' already exists"
        )
    
    return await TagService.create_tag(data, db)


@router.get("", response_model=List[TagOut])
async def get_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get list of tags with pagination"""
    return await TagService.get_tags(skip, limit, db)


@router.get("/{tag_id}", response_model=TagOut)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a tag by ID"""
    tag = await TagService.get_tag_by_id(tag_id, db)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found"
        )
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a tag"""
    success = await TagService.delete_tag(tag_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found"
        )
    return None
