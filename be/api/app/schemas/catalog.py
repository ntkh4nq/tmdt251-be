from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

# --- Category ---
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryOut(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Tag ---
class TagBase(BaseModel):
    name: str = Field(..., max_length=255)

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Ingredient ---
class IngredientBase(BaseModel):
    name: str = Field(..., max_length=255)
    unit: str = Field(..., max_length=50)
    price_per_unit: float
    calories_per_unit: float
    stock_quantity: float

class IngredientCreate(IngredientBase):
    pass

class IngredientOut(IngredientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Product Variant ---
class ProductVariantBase(BaseModel):
    name: str = Field(..., max_length=255)
    sku: str = Field(..., max_length=255)
    price: float
    stock: float

class ProductVariantCreate(ProductVariantBase):
    pass

class ProductVariantOut(ProductVariantBase):
    id: int
    product_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Product Ingredient ---
class ProductIngredientBase(BaseModel):
    ingredient_id: int
    min_percentage: Optional[float] = None
    max_percentage: Optional[float] = None

class ProductIngredientCreate(ProductIngredientBase):
    pass

class ProductIngredientOut(ProductIngredientBase):
    id: int
    product_id: int
    ingredient: Optional[IngredientOut] = None
    model_config = ConfigDict(from_attributes=True)

# --- Product ---
class Nutrition(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: Optional[float] = 0

class ProductBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str
    price: float
    stock: int
    model_file: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    category_id: int
    nutritions: Optional[Nutrition] = None

class ProductCreate(ProductBase):
    tags: Optional[List[int]] = [] # List of Tag IDs
    ingredients: Optional[List[ProductIngredientCreate]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    model_file: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None
    nutritions: Optional[Nutrition] = None
    tags: Optional[List[int]] = None

class ProductOut(ProductBase):
    id: int
    category: Optional[CategoryOut] = None
    # product_tags: List[TagOut] # logic might be needed to flatten
    variants: List[ProductVariantOut] = []
    ingredients: List[ProductIngredientOut] = []
    model_config = ConfigDict(from_attributes=True)
