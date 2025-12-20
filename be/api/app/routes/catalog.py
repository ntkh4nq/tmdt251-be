from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.dependencies import get_db, get_current_user
from app.models.catalog_product import Category, Product, ProductVariant, Ingredient, Tag
from app.schemas.catalog import (
    CategoryCreate, CategoryUpdate, CategoryOut,
    ProductCreate, ProductUpdate, ProductOut,
    ProductVariantCreate, ProductVariantOut,
    IngredientCreate, IngredientOut, TagOut
)
from app.services.utils import commit_to_db

router = APIRouter(tags=["Catalog"])

# --- Categories ---
@router.post("/categories", response_model=CategoryOut)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    new_category = Category(**data.model_dump())
    db.add(new_category)
    await commit_to_db(db)
    await db.refresh(new_category)
    return new_category

@router.get("/categories", response_model=List[CategoryOut])
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/categories/{id}", response_model=CategoryOut)
async def get_category(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# --- Products ---
@router.post("/products", response_model=ProductOut)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    # Handle relations if needed, simple dump for now
    product_data = data.model_dump(exclude={"tags", "ingredients"})
    new_product = Product(**product_data)
    db.add(new_product)
    await commit_to_db(db)
    await db.refresh(new_product)
    return new_product

@router.get("/products", response_model=List[ProductOut])
async def get_products(
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[int] = None, 
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Product)
    if category_id:
        query = query.where(Product.category_id == category_id)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/products/{id}", response_model=ProductOut)
async def get_product(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# --- Variants ---
@router.get("/products/{product_id}/variants", response_model=List[ProductVariantOut])
async def get_product_variants(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductVariant).where(ProductVariant.product_id == product_id))
    return result.scalars().all()

@router.post("/products/{product_id}/variants", response_model=ProductVariantOut)
async def create_product_variant(product_id: int, data: ProductVariantCreate, db: AsyncSession = Depends(get_db)):
    # Ensure product_id matches
    variant_data = data.model_dump()
    variant_data["product_id"] = product_id # Override if passed incorrectly or needed
    # Wait, pydantic model might not have product_id in Create, but Base does.
    # Schema check: ProductVariantCreate is ProductVariantBase (name, sku, price, stock). It does NOT have product_id.
    # ProductVariant (model) has product_id.
    
    new_variant = ProductVariant(**variant_data, product_id=product_id)
    db.add(new_variant)
    await commit_to_db(db)
    await db.refresh(new_variant)
    return new_variant

# --- Ingredients ---
@router.get("/ingredients", response_model=List[IngredientOut])
async def get_ingredients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ingredient).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/ingredients", response_model=IngredientOut)
async def create_ingredient(data: IngredientCreate, db: AsyncSession = Depends(get_db)):
    new_ing = Ingredient(**data.model_dump())
    db.add(new_ing)
    await commit_to_db(db)
    await db.refresh(new_ing)
    return new_ing

# --- Tags ---
@router.get("/tags", response_model=List[TagOut])
async def get_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag))
    return result.scalars().all()
