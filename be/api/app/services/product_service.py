from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from app.models.product import Product, ProductTag, ProductIngredient
from app.schemas.catalog import ProductCreate, ProductUpdate
from app.services.utils import commit_to_db


class ProductService:
    """Service layer for Product operations"""

    @staticmethod
    async def create_product(data: ProductCreate, db: AsyncSession) -> Product:
        """Create a new product with tags and ingredients"""
        # Extract relations
        product_data = data.model_dump(exclude={"tags", "ingredients"})
        new_product = Product(**product_data)
        db.add(new_product)
        await commit_to_db(db)
        await db.refresh(new_product)

        # Add tags if provided
        if data.tags:
            for tag_id in data.tags:
                product_tag = ProductTag(product_id=new_product.id, tag_id=tag_id)
                db.add(product_tag)

        # Add ingredients if provided
        if data.ingredients:
            for ing_data in data.ingredients:
                product_ing = ProductIngredient(
                    product_id=new_product.id,
                    **ing_data.model_dump()
                )
                db.add(product_ing)

        await commit_to_db(db)
        await db.refresh(new_product)
        return new_product

    @staticmethod
    async def get_products(
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        db: AsyncSession = None
    ) -> List[Product]:
        """Get list of products with filters and pagination"""
        query = select(Product)

        # Apply filters
        if category_id:
            query = query.where(Product.category_id == category_id)
        if search:
            query = query.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        if is_active is not None:
            query = query.where(Product.is_active == is_active)

        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_product_by_id(product_id: int, db: AsyncSession) -> Optional[Product]:
        """Get a product by ID with all relations"""
        result = await db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_product_by_name(name: str, db: AsyncSession) -> Optional[Product]:
        """Get a product by name"""
        result = await db.execute(select(Product).where(Product.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_product(
        product_id: int,
        data: ProductUpdate,
        db: AsyncSession
    ) -> Optional[Product]:
        """Update a product"""
        product = await ProductService.get_product_by_id(product_id, db)
        if not product:
            return None

        # Update basic fields
        update_data = data.model_dump(exclude={"tags"}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        # Update tags if provided
        if data.tags is not None:
            # Remove old tags
            await db.execute(
                select(ProductTag).where(ProductTag.product_id == product_id)
            )
            old_tags = (await db.execute(
                select(ProductTag).where(ProductTag.product_id == product_id)
            )).scalars().all()
            for tag in old_tags:
                await db.delete(tag)

            # Add new tags
            for tag_id in data.tags:
                product_tag = ProductTag(product_id=product_id, tag_id=tag_id)
                db.add(product_tag)

        await commit_to_db(db)
        await db.refresh(product)
        return product

    @staticmethod
    async def update_product_stock(
        product_id: int,
        stock: int,
        db: AsyncSession
    ) -> Optional[Product]:
        """Update product stock"""
        product = await ProductService.get_product_by_id(product_id, db)
        if not product:
            return None

        product.stock = stock
        await commit_to_db(db)
        await db.refresh(product)
        return product

    @staticmethod
    async def delete_product(product_id: int, db: AsyncSession) -> bool:
        """Delete a product (soft delete by setting is_active=False)"""
        product = await ProductService.get_product_by_id(product_id, db)
        if not product:
            return False

        product.is_active = False
        await commit_to_db(db)
        return True

    @staticmethod
    async def hard_delete_product(product_id: int, db: AsyncSession) -> bool:
        """Permanently delete a product"""
        product = await ProductService.get_product_by_id(product_id, db)
        if not product:
            return False

        await db.delete(product)
        await commit_to_db(db)
        return True
