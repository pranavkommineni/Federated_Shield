"""Pydantic schemas for User management and Role-Based Access Control."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from app.schemas.org import OrgResponse


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    role: str = Field(..., pattern="^(admin|org_admin|staff|customer)$")
    org_id: Optional[int] = None
    department: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    organization: Optional[OrgResponse] = None

    model_config = ConfigDict(from_attributes=True)


class SwitchRoleRequest(BaseModel):
    user_id: Optional[int] = None
    role: str = Field(..., pattern="^(admin|org_admin|staff|customer)$")
    org_id: Optional[int] = None
