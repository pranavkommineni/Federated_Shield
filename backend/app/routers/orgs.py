"""Router for managing simulated client organizations."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.org import Organization
from app.schemas.org import OrgRegister, OrgResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orgs", tags=["Organizations"])


@router.post(
    "/register",
    response_model=OrgResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new simulated organization",
    description="Creates a new organization (client node) with initial status 'idle'.",
)
def register_organization(org_in: OrgRegister, db: Session = Depends(get_db)) -> Organization:
    """Register a new simulated client organization."""
    existing = db.query(Organization).filter(Organization.name == org_in.name.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization with name '{org_in.name}' is already registered.",
        )

    new_org = Organization(
        name=org_in.name.strip(),
        description=org_in.description,
        status="idle",
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    logger.info(f"Registered new organization: {new_org.name} (ID: {new_org.id})")
    return new_org


@router.get(
    "",
    response_model=List[OrgResponse],
    summary="List all registered organizations",
    description="Returns all registered simulated organizations along with their current status ('idle', 'training', 'done', 'offline').",
)
def list_organizations(db: Session = Depends(get_db)) -> List[Organization]:
    """List all registered organizations."""
    return db.query(Organization).order_by(Organization.id.asc()).all()


@router.get(
    "/{org_id}",
    response_model=OrgResponse,
    summary="Get organization details",
    description="Retrieve full details for a specific organization by ID.",
)
def get_organization(org_id: int, db: Session = Depends(get_db)) -> Organization:
    """Get single organization by ID."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with ID {org_id} not found.",
        )
    return org


@router.delete(
    "/{org_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an organization",
    description="Remove an organization from the system.",
)
def delete_organization(org_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete organization by ID."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with ID {org_id} not found.",
        )

    db.delete(org)
    db.commit()
    logger.info(f"Deleted organization ID: {org_id}")
    return {"message": f"Organization '{org.name}' (ID: {org_id}) deleted successfully."}
