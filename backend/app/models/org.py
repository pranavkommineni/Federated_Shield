"""SQLAlchemy model for simulated organizations (clients)."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class Organization(Base):
    """Represents a simulated organization or participating edge node in the FL network."""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(String(50), default="idle", nullable=False)  # 'idle', 'training', 'done', 'offline'
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}', status='{self.status}')>"
