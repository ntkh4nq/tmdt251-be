from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.product_variant import ProductVariant
from app.schemas.catalog import ProductVariantCreate
from app.services.utils import commit_to_db


class VariantService:
    """Service layer for ProductVariant operations"""

    @staticmethod
    async def create_variant(
        product_id: int,
        data: ProductVariantCreate,
        db: AsyncSession
    ) -> ProductVariant:
        """Create a new product variant"""
        variant_data = data.model_dump()
        new_variant = ProductVariant(**variant_data, product_id=product_id)
        db.add(new_variant)
        await commit_to_db(db)
        await db.refresh(new_variant)
        return new_variant

    @staticmethod
    async def get_variants_by_product(
        product_id: int,
        db: AsyncSession
    ) -> List[ProductVariant]:
        """Get all variants for a product"""
        result = await db.execute(
            select(ProductVariant).where(ProductVariant.product_id == product_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_variant_by_id(variant_id: int, db: AsyncSession) -> Optional[ProductVariant]:
        """Get a variant by ID"""
        result = await db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_variant_by_sku(sku: str, db: AsyncSession) -> Optional[ProductVariant]:
        """Get a variant by SKU"""
        result = await db.execute(select(ProductVariant).where(ProductVariant.sku == sku))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_variant_stock(
        variant_id: int,
        stock: float,
        db: AsyncSession
    ) -> Optional[ProductVariant]:
        """Update variant stock"""
        variant = await VariantService.get_variant_by_id(variant_id, db)
        if not variant:
            return None

        variant.stock = stock
        await commit_to_db(db)
        await db.refresh(variant)
        return variant

    @staticmethod
    async def delete_variant(variant_id: int, db: AsyncSession) -> bool:
        """Delete a variant"""
        variant = await VariantService.get_variant_by_id(variant_id, db)
        if not variant:
            return False

        await db.delete(variant)
        await commit_to_db(db)
        return True
