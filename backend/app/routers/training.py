"""Router for federated training lifecycle management and history retrieval."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.org import Organization
from app.models.round import RoundHistory
from app.schemas.round import (
    TrainingStartRequest,
    TrainingStartResponse,
    TrainingStopResponse,
    TrainingStatusResponse,
    RoundMetricResponse,
)
from app.services.training_engine import training_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/training", tags=["Training"])


@router.post(
    "/start",
    response_model=TrainingStartResponse,
    status_code=status.HTTP_200_OK,
    summary="Start a federated training run",
    description="Initiates a new federated training run with the specified number of rounds and participating organizations.",
)
async def start_training(
    payload: TrainingStartRequest,
    db: Session = Depends(get_db),
) -> TrainingStartResponse:
    """Initiate a federated training session."""
    if training_engine.is_training:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A federated training run is already active. Stop the current run before starting a new one.",
        )

    participating_org_names: List[str] = []

    # 1. Resolve orgs by explicit IDs if provided
    if payload.org_ids:
        orgs = db.query(Organization).filter(Organization.id.in_(payload.org_ids)).all()
        if not orgs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="None of the specified organization IDs were found.",
            )
        participating_org_names = [o.name for o in orgs]

    # 2. Resolve orgs by explicit names if provided
    elif payload.org_names:
        orgs = db.query(Organization).filter(Organization.name.in_(payload.org_names)).all()
        if not orgs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="None of the specified organization names were found.",
            )
        participating_org_names = [o.name for o in orgs]

    # 3. Otherwise, select all registered orgs in the DB
    else:
        all_orgs = db.query(Organization).all()
        if not all_orgs:
            # Auto-seed default hospital demo clients if table is empty
            default_names = ["Hospital Alpha", "Medical Center Beta", "Healthcare Node Gamma"]
            for name in default_names:
                db_org = Organization(name=name, description="Auto-seeded simulated node", status="idle")
                db.add(db_org)
            db.commit()
            all_orgs = db.query(Organization).all()

        participating_org_names = [o.name for o in all_orgs]

    try:
        run_id = await training_engine.start_training(
            rounds=payload.rounds,
            org_names=participating_org_names,
            target_accuracy=payload.target_accuracy,
            max_epsilon=payload.max_epsilon,
        )
        return TrainingStartResponse(
            message="Federated training session started successfully.",
            run_id=run_id,
            total_rounds=payload.rounds,
            participating_orgs=participating_org_names,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start training: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start training: {str(e)}",
        )


@router.post(
    "/stop",
    response_model=TrainingStopResponse,
    status_code=status.HTTP_200_OK,
    summary="Stop the active training run",
    description="Signals the active federated training run to halt gracefully.",
)
async def stop_training() -> TrainingStopResponse:
    """Stop the ongoing federated training run."""
    result = await training_engine.stop_training()
    return TrainingStopResponse(
        message=result["message"],
        run_id=result.get("run_id"),
        stopped_at_round=result.get("stopped_at_round"),
        status=result["status"],
    )


@router.get(
    "/status",
    response_model=TrainingStatusResponse,
    summary="Get current training coordinator status",
    description="Returns whether training is currently running, current round number, total rounds, active orgs, and latest metrics.",
)
def get_training_status() -> TrainingStatusResponse:
    """Get the live status of the federated training coordinator."""
    status_data = training_engine.get_status()
    return TrainingStatusResponse(
        is_training=status_data["is_training"],
        status=status_data["status"],
        run_id=status_data["run_id"],
        current_round=status_data["current_round"],
        total_rounds=status_data["total_rounds"],
        active_orgs=status_data["active_orgs"],
        latest_accuracy=status_data["latest_accuracy"],
        latest_loss=status_data["latest_loss"],
        cumulative_epsilon=status_data["cumulative_epsilon"],
    )


@router.get(
    "/history",
    response_model=List[RoundMetricResponse],
    summary="Get historical training rounds",
    description="Retrieve round history and metrics across past training runs from SQLite.",
)
def get_training_history(
    run_id: Optional[str] = Query(None, description="Filter history by specific run ID"),
    limit: int = Query(50, ge=1, le=500, description="Max number of records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
) -> List[RoundMetricResponse]:
    """Retrieve historical round metrics from SQLite database."""
    query = db.query(RoundHistory)
    if run_id:
        query = query.filter(RoundHistory.run_id == run_id)

    rounds = query.order_by(RoundHistory.id.desc()).offset(offset).limit(limit).all()

    # Map ORM objects to response schemas
    return [
        RoundMetricResponse(
            id=r.id,
            run_id=r.run_id,
            round_number=r.round_number,
            total_rounds=r.total_rounds,
            accuracy=r.accuracy,
            loss=r.loss,
            epsilon_spent=r.epsilon_spent,
            cumulative_epsilon=r.cumulative_epsilon,
            participating_orgs=r.participating_orgs,
            org_statuses=r.org_statuses,
            duration_seconds=r.duration_seconds,
            status=r.status,
            timestamp=r.timestamp,
        )
        for r in rounds
    ]
