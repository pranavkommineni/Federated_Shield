"""SQLAlchemy model for Role-Based Access Control (Admin, Org Admin, Staff, Customer)."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """Represents a platform user with assigned role and organization affiliation."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(String(30), nullable=False, default="staff")  # 'admin', 'org_admin', 'staff', 'customer'
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    department = Column(String(100), nullable=True)  # e.g., 'Cardiology', 'Oncology', 'Data Science', 'Clinical Audit'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to Organization
    organization = relationship("Organization", backref="users", lazy="joined")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}', org_id={self.org_id})>"
