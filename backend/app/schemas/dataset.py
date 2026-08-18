"""Pydantic schemas for datasets and clinical sample submissions."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ClinicalSampleCreate(BaseModel):
    org_id: int
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., pattern="^(Male|Female|Other)$")
    blood_pressure_sys: int = Field(..., ge=60, le=250)
    cholesterol: int = Field(..., ge=80, le=500)
    glucose: int = Field(..., ge=40, le=400)
    heart_rate: int = Field(..., ge=40, le=220)
    target_risk: float = Field(..., ge=0.0, le=1.0, description="Ground truth disease risk score (0-1)")
    contributed_by: Optional[str] = "staff_worker"


class ClinicalSampleResponse(ClinicalSampleCreate):
    id: int
    patient_identifier_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LocalDatasetResponse(BaseModel):
    id: int
    org_id: int
    name: str
    modality: str
    sample_count: int
    privacy_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
