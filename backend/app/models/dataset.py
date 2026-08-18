"""SQLAlchemy model for local client datasets and clinical sample records."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class LocalDataset(Base):
    """Represents a private edge dataset silo belonging to an organization."""

    __tablename__ = "local_datasets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    modality = Column(String(50), default="tabular_clinical", nullable=False)  # 'tabular_clinical', 'ecg', 'xray'
    sample_count = Column(Integer, default=0, nullable=False)
    features_schema = Column(Text, default="[]", nullable=False)
    privacy_status = Column(String(50), default="noise_calibrated", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    organization = relationship("Organization", backref="datasets")


class ClinicalSample(Base):
    """Sample clinical record uploaded or contributed by staff to a local dataset."""

    __tablename__ = "clinical_samples"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    patient_identifier_hash = Column(String(64), nullable=False)  # Pseudonymized hash
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    blood_pressure_sys = Column(Integer, nullable=False)
    cholesterol = Column(Integer, nullable=False)
    glucose = Column(Integer, nullable=False)
    heart_rate = Column(Integer, nullable=False)
    target_risk = Column(Float, nullable=False)  # 0.0 to 1.0 (diagnosis ground truth)
    contributed_by = Column(String(50), nullable=True)  # Username of staff
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
