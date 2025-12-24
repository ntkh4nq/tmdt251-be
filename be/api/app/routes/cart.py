from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.cart import CartOut, CartItemCreate, CartItemUpdate, CartItemOut
from app.services.utils import commit_to_db

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])


@router.get("", response_model=CartOut)
async def get_my_cart(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # Find active cart
    query = select(Cart).where(Cart.user_id == current_user.id)
    result = await db.execute(query)
    cart = result.scalar_one_or_none()

    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        await commit_to_db(db)
        await db.refresh(cart)

    return cart


@router.post("/items", response_model=CartItemOut)
async def add_item_to_cart(
    item_data: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ensure cart exists
    query = select(Cart).where(Cart.user_id == current_user.id)
    result = await db.execute(query)
    cart = result.scalar_one_or_none()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        await commit_to_db(db)
        await db.refresh(cart)

    # Retrieve all items for this product in the cart to check for matching configuration
    query_items = select(CartItem).where(
        and_(CartItem.cart_id == cart.id, CartItem.product_id == item_data.product_id)
    )
    result_items = await db.execute(query_items)
    existing_items = result_items.scalars().all()

    # Check for matching configuration
    matching_item = None
    for item in existing_items:
        # Compare JSONs (dictionaries)
        if item.custom_configuration == item_data.custom_configuration:
            matching_item = item
            break

    if matching_item:
        matching_item.quantity += item_data.quantity
        await commit_to_db(db)
        await db.refresh(matching_item)
        return matching_item
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            custom_configuration=item_data.custom_configuration,
        )
        db.add(new_item)
        await commit_to_db(db)
        await db.refresh(new_item)
        return new_item


@router.put("/items/{item_id}", response_model=CartItemOut)
async def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify item belongs to user's cart
    # Join with Cart to check user_id
    query = (
        select(CartItem)
        .join(Cart)
        .where(and_(CartItem.id == item_id, Cart.user_id == current_user.id))
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    item.quantity = data.quantity
    await commit_to_db(db)
    await db.refresh(item)
    return item


@router.delete("/items/{item_id}")
async def remove_cart_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(CartItem)
        .join(Cart)
        .where(and_(CartItem.id == item_id, Cart.user_id == current_user.id))
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if item:
        await db.delete(item)
        await commit_to_db(db)

    return {"message": "Item removed"}