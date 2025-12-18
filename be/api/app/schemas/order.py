from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timezone, timedelta
from typing import List, Optional

class PaymentURLRequest(BaseModel):
    vnp_Version: str = Field(min_length=1, max_length=8, default="2.1.0")
    vnp_Command: str = Field(min_length=1, max_length=16, default="pay")
    #vnp_TmnCode: str = Field(..., min_length=8, max_length=8)
    vnp_Amount: str = Field(..., min_length=1, max_length=12)
    vnp_BankCode: Optional[str] = Field(None, min_length=3, max_length=20)
    vnp_CreateDate: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    vnp_CurrCode: str = Field(min_length=3, max_length=3, default="VND")
    vnp_IpAddr: str = Field(min_length=7, max_length=45, default="1.54.206.73")
    vnp_Locale: str = Field(min_length=2, max_length=5, default="vn")
    vnp_OrderInfo: str = Field(..., min_length=1, max_length=255)
    vnp_OrderType: str = Field(min_length=1, max_length=100, default="other")
    vnp_ReturnUrl: str = Field(..., min_length=10, max_length=255)
    #vnp_ExpiredDate: datetime = Field(..., default_factory=datetime.now())
    vnp_TxnRef: str = Field(..., min_length=1, max_length=100)