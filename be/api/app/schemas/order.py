from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any


# --- Existing Payment Schemas ---
class PaymentURLRequest(BaseModel):
    vnp_Version: str = Field(min_length=1, max_length=8, default="2.1.0")
    vnp_Command: str = Field(min_length=1, max_length=16, default="pay")
    vnp_Amount: str = Field(..., min_length=1, max_length=12)
    vnp_BankCode: Optional[str] = Field(None, min_length=3, max_length=20)
    vnp_CreateDate: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    vnp_CurrCode: str = Field(min_length=3, max_length=3, default="VND")
    vnp_IpAddr: str = Field(min_length=7, max_length=45, default="1.54.206.73")
    vnp_Locale: str = Field(min_length=2, max_length=5, default="vn")
    vnp_OrderInfo: str = Field(..., min_length=1, max_length=255)
    vnp_OrderType: str = Field(min_length=1, max_length=100, default="other")
    vnp_ReturnUrl: str = Field(
        min_length=10,
        max_length=255,
        default="http://localhost:8000/order/payment_return",
    )
    vnp_TxnRef: str = Field(..., min_length=1, max_length=100)


class PaymentUrlOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    payment_url: str


# --- Order Schemas ---
class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    custom_configuration: Optional[Dict[str, Any]] = None
    id: int
    model_config = ConfigDict(from_attributes=True)


class ShipmentOut(BaseModel):
    id: int
    tracking_code: Optional[str]
    courier: Optional[str]
    status: str
    model_config = ConfigDict(from_attributes=True)


class PaymentOut(BaseModel):
    id: int
    amount: float
    status: str
    method: str
    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    id: int
    user_id: int
    address_id: int
    status: str
    payment_status: str
    subtotal: float
    total_amount: float
    created_at: datetime

    items: List[OrderItemOut] = []
    shipments: List[ShipmentOut] = []
    payments: List[PaymentOut] = []

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    address_id: int
    # Items are usually taken from Cart, but for API flexibility we might allow passing checks
    # For now, let's assume we create from Cart, or pass simple items?
    # User said "based on current code".
    # I'll stick to a simple creation triggering from Cart if no items passed, or something?
    # Or just standard "create order from cart" endpoint.
    pass


class OrderStatusUpdate(BaseModel):
    status: str
