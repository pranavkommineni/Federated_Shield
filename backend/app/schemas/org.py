"""Pydantic schemas for organization endpoints and data validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class OrgBase(BaseModel):
    """Base fields for an organization."""
    name: str = Field(..., min_length=2, max_length=100, description="Unique identifier/name for the organization")
    description: Optional[str] = Field(None, max_length=255, description="Optional description of the client node")


class OrgRegister(OrgBase):
    """Schema for registering a new simulated organization."""
    pass


class OrgUpdateStatus(BaseModel):
    """Schema for manually updating an organization's status."""
    status: str = Field(..., pattern="^(idle|training|done|offline)$", description="New status for the organization")


class OrgResponse(OrgBase):
    """Response schema representing an organization with its current state."""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
