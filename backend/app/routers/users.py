"""Router for User Management, Role-Based Access Control, and Role Switching."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.org import Organization
from app.schemas.user import UserCreate, UserResponse, SwitchRoleRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users & Access Control"])


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List all users",
    description="Retrieve all registered platform users with their roles and organization links.",
)
def list_users(
    role: Optional[str] = Query(None, description="Filter by role: admin, org_admin, staff, customer"),
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
    db: Session = Depends(get_db),
) -> List[User]:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if org_id:
        query = query.filter(User.org_id == org_id)
    return query.all()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Register a new user account with specified role and organization assignment.",
)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    existing = db.query(User).filter(
        (User.username == user_in.username.strip()) | (User.email == user_in.email.strip())
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered.",
        )

    if user_in.org_id:
        org = db.query(Organization).filter(Organization.id == user_in.org_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assigned organization ID {user_in.org_id} does not exist.",
            )

    new_user = User(
        username=user_in.username.strip(),
        full_name=user_in.full_name.strip(),
        email=user_in.email.strip(),
        role=user_in.role,
        org_id=user_in.org_id,
        department=user_in.department,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"Registered user: {new_user.username} (Role: {new_user.role})")
    return new_user


@router.get(
    "/active",
    response_model=UserResponse,
    summary="Get active mock user profile for testing",
)
def get_active_user(
    role: str = Query("admin", pattern="^(admin|org_admin|staff|customer)$"),
    org_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
) -> User:
    """Returns a representative user for testing the selected role."""
    query = db.query(User).filter(User.role == role)
    if org_id and role in ["org_admin", "staff"]:
        user = query.filter(User.org_id == org_id).first()
        if user:
            return user

    user = query.first()
    if not user:
        # Fallback to any user
        user = db.query(User).first()
        if not user:
            raise HTTPException(status_code=404, detail="No users found in database.")
    return user
