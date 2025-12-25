from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.dependencies import get_db
from app.schemas.catalog import ProductCreate, ProductUpdate, ProductOut
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.services.cloudinary_service import CloudinaryService

router = APIRouter(prefix="/catalog/products", tags=["Products"])

@router.post("/upload-image")
async def upload_product_image(file: UploadFile = File(...)):
    """
    Upload product image to Cloudinary
    
    - Accepts: JPEG, PNG, WEBP
    - Max size: 5MB
    - Returns: image URL and metadata
    """
    result = await CloudinaryService.upload_image(file, folder="products")
    return {
        "success": True,
        "image_url": result["url"],
        "public_id": result["public_id"],
        "width": result["width"],
        "height": result["height"]
    }

@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new product"""
    # Check if product name already exists
    existing = await ProductService.get_product_by_name(data.name, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with name '{data.name}' already exists"
        )
    
    # Verify category exists
    category = await CategoryService.get_category_by_id(data.category_id, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {data.category_id} not found"
        )
    
    return await ProductService.create_product(data, db)


@router.get("", response_model=List[ProductOut])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of products with filters and pagination
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Max number of records to return (default: 100, max: 100)
    - **category_id**: Filter by category ID
    - **search**: Search in product name and description
    - **is_active**: Filter by active status (default: True)
    """
    return await ProductService.get_products(
        skip=skip,
        limit=limit,
        category_id=category_id,
        search=search,
        is_active=is_active,
        db=db
    )


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a product by ID with all details"""
    product = await ProductService.get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a product"""
    # Check if new name conflicts
    if data.name:
        existing = await ProductService.get_product_by_name(data.name, db)
        if existing and existing.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with name '{data.name}' already exists"
            )
    
    # Verify category exists if updating
    if data.category_id:
        category = await CategoryService.get_category_by_id(data.category_id, db)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {data.category_id} not found"
            )
    
    product = await ProductService.update_product(product_id, data, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return product


@router.patch("/{product_id}/stock")
async def update_product_stock(
    product_id: int,
    stock: int = Query(..., ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Update product stock quantity"""
    product = await ProductService.update_product_stock(product_id, stock, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return {"message": "Stock updated successfully", "stock": product.stock}


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    hard_delete: bool = Query(False, description="Permanently delete product"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a product (soft delete by default, set hard_delete=true for permanent deletion)
    """
    if hard_delete:
        success = await ProductService.hard_delete_product(product_id, db)
    else:
        success = await ProductService.delete_product(product_id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return None



