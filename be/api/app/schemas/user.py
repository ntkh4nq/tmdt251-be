from pydantic import BaseModel, EmailStr, ConfigDict, Field, computed_field
from datetime import datetime
from typing import List, Optional


class GoogleUserInfo(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None
    google_id: str


class UserBase(BaseModel):
    fullname: str = Field(
        ..., min_length=1, max_length=255, description="User full name"
    )
    email: EmailStr = Field(..., description="Unique email addr")
    phone: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Optional phone number"
    )


# register
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Plaintext password")


# login
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    fullname: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=8, description="New password")


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    addresses: List["AddressOut"] = []


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    refresh_token: str
    device_info: str
    expired_at: datetime


class AddressBase(BaseModel):
    label: str = Field(..., min_length=1, max_length=255)
    street: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=255)
    province: str = Field(..., min_length=1, max_length=255)
    postal_code: str = Field(..., min_length=1, max_length=10)
    is_default: bool = Field(True, description="default address?")


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    label: Optional[str] = Field(None, min_length=1, max_length=255)
    street: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=255)
    province: Optional[str] = Field(None, min_length=1, max_length=255)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=10)
    is_default: Optional[bool] = None


class AddressOut(AddressBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)


class RoleCreate(RoleBase):
    pass


class RoleOut(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserRoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    role_id: int
    role: RoleOut


class UserAdminOut(UserOut):
    user_roles: List["UserRoleOut"] = Field(default=[], exclude=True)

    @computed_field
    def role(self) -> str:
        if not self.user_roles:
            return "user"

        # Check for admin
        for ur in self.user_roles:
            if ur.role.name == "admin":
                return "admin"

        # Fallback to first role if exists
        if self.user_roles and self.user_roles[0].role:
            return self.user_roles[0].role.name

        return "user"
