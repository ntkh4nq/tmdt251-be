from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from .catalog import ProductOut


class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    custom_configuration: Optional[Dict[str, Any]] = None


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemOut(CartItemBase):
    id: int
    cart_id: int
    product: Optional[ProductOut] = None
    model_config = ConfigDict(from_attributes=True)


class CartOut(BaseModel):
    id: int
    user_id: int
    items: List[CartItemOut] = []
    # Computed fields like total_price could be added here or in frontend
    model_config = ConfigDict(from_attributes=True)
