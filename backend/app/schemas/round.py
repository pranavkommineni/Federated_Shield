"""Pydantic schemas for federated training control, history metrics, and WebSocket events."""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class TrainingStartRequest(BaseModel):
    """Payload to initiate a new federated training run."""
    rounds: int = Field(5, ge=1, le=100, description="Total number of federated rounds to execute")
    org_ids: Optional[List[int]] = Field(None, description="List of organization IDs to participate")
    org_names: Optional[List[str]] = Field(None, description="List of organization names to participate")
    target_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Optional early-stopping accuracy threshold")
    max_epsilon: Optional[float] = Field(None, gt=0.0, description="Maximum allowable Differential Privacy epsilon budget")


class TrainingStartResponse(BaseModel):
    """Response returned when a training run is successfully triggered."""
    message: str
    run_id: str
    total_rounds: int
    participating_orgs: List[str]


class TrainingStopResponse(BaseModel):
    """Response returned when an active training run is requested to halt."""
    message: str
    run_id: Optional[str] = None
    stopped_at_round: Optional[int] = None
    status: str


class TrainingStatusResponse(BaseModel):
    """Response representing real-time status of the federated training coordinator."""
    is_training: bool
    status: str = Field(..., description="'idle', 'running', 'stopping', 'completed', 'aborted'")
    run_id: Optional[str] = None
    current_round: int = 0
    total_rounds: int = 0
    active_orgs: List[str] = []
    latest_accuracy: Optional[float] = None
    latest_loss: Optional[float] = None
    cumulative_epsilon: Optional[float] = None


class RoundMetricResponse(BaseModel):
    """Historical metric entry for a single completed round."""
    id: int
    run_id: str
    round_number: int
    total_rounds: int
    accuracy: float
    loss: float
    epsilon_spent: float
    cumulative_epsilon: float
    participating_orgs: List[str]
    org_statuses: Dict[str, str]
    duration_seconds: float
    status: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class WebSocketEvent(BaseModel):
    """Schema for structured messages broadcast over the WebSocket connection."""
    event: str = Field(..., description="Event type: 'training_started', 'round_complete', 'training_completed', 'training_stopped', 'status_update', 'ping'")
    run_id: Optional[str] = None
    round: Optional[int] = None
    total_rounds: Optional[int] = None
    accuracy: Optional[float] = None
    loss: Optional[float] = None
    epsilon_spent: Optional[float] = None
    cumulative_epsilon: Optional[float] = None
    org_statuses: Optional[Dict[str, str]] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    message: Optional[str] = None
