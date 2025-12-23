from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_db
from app.schemas.catalog import ProductVariantCreate, ProductVariantOut
from app.services.variant_service import VariantService
from app.services.product_service import ProductService

router = APIRouter(prefix="/catalog/products/{product_id}/variants", tags=["Product Variants"])


@router.get("", response_model=List[ProductVariantOut])
async def get_product_variants(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all variants for a product"""
    # Verify product exists
    product = await ProductService.get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    return await VariantService.get_variants_by_product(product_id, db)


@router.post("", response_model=ProductVariantOut, status_code=status.HTTP_201_CREATED)
async def create_product_variant(
    product_id: int,
    data: ProductVariantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new variant for a product"""
    # Verify product exists
    product = await ProductService.get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    # Check if SKU already exists
    existing = await VariantService.get_variant_by_sku(data.sku, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Variant with SKU '{data.sku}' already exists"
        )
    
    return await VariantService.create_variant(product_id, data, db)


@router.patch("/{variant_id}/stock")
async def update_variant_stock(
    product_id: int,
    variant_id: int,
    stock: float = Query(..., ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Update variant stock quantity"""
    variant = await VariantService.get_variant_by_id(variant_id, db)
    if not variant or variant.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with id {variant_id} not found for product {product_id}"
        )
    
    variant = await VariantService.update_variant_stock(variant_id, stock, db)
    return {"message": "Variant stock updated successfully", "stock": variant.stock}


@router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variant(
    product_id: int,
    variant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a product variant"""
    variant = await VariantService.get_variant_by_id(variant_id, db)
    if not variant or variant.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with id {variant_id} not found for product {product_id}"
        )
    
    success = await VariantService.delete_variant(variant_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with id {variant_id} not found"
        )
    return None
