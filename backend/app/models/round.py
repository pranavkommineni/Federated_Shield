"""SQLAlchemy model for tracking federated training rounds and privacy metrics."""

import json
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database import Base


class RoundHistory(Base):
    """Represents the metrics and status recorded for a completed federated training round."""

    __tablename__ = "round_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_id = Column(String(64), index=True, nullable=False)
    round_number = Column(Integer, nullable=False)
    total_rounds = Column(Integer, nullable=False)
    accuracy = Column(Float, nullable=False)
    loss = Column(Float, nullable=False)
    epsilon_spent = Column(Float, nullable=False)
    cumulative_epsilon = Column(Float, nullable=False)
    _participating_orgs = Column("participating_orgs", Text, nullable=False, default="[]")
    _org_statuses = Column("org_statuses", Text, nullable=False, default="{}")
    duration_seconds = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False, default="completed")  # 'completed', 'aborted', 'failed'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    @property
    def participating_orgs(self) -> List[str]:
        """Deserialize participating_orgs JSON string into a Python list."""
        try:
            return json.loads(self._participating_orgs) if self._participating_orgs else []
        except Exception:
            return []

    @participating_orgs.setter
    def participating_orgs(self, value: List[str]) -> None:
        """Serialize participating_orgs list into a JSON string."""
        self._participating_orgs = json.dumps(value if value is not None else [])

    @property
    def org_statuses(self) -> Dict[str, str]:
        """Deserialize org_statuses JSON string into a Python dict."""
        try:
            return json.loads(self._org_statuses) if self._org_statuses else {}
        except Exception:
            return {}

    @org_statuses.setter
    def org_statuses(self, value: Dict[str, str]) -> None:
        """Serialize org_statuses dict into a JSON string."""
        self._org_statuses = json.dumps(value if value is not None else {})

    def __repr__(self) -> str:
        return (
            f"<RoundHistory(run_id='{self.run_id}', round={self.round_number}/{self.total_rounds}, "
            f"acc={self.accuracy:.4f}, loss={self.loss:.4f}, eps={self.cumulative_epsilon:.3f})>"
        )
