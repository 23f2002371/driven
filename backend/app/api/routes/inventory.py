"""Inventory endpoints.

- ``POST   /equipment``              - create a piece of equipment (club admin only).
- ``PATCH  /equipment/{equipment_id}`` - update a piece of equipment (club admin only).
- ``POST   /equipment/borrow``       - borrow equipment (student only).
- ``DELETE /borrow-details/{borrow_detail_id}`` - return borrowed equipment (club admin only).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select

from app.api.deps import DbSession, get_current_user, require_roles
from app.models.inventory import BorrowDetail, Equipment
from app.models.student import Student
from app.models.user import User
from app.schemas.inventory import (
    BorrowDetailResponse,
    BorrowEquipmentRequest,
    EquipmentCreate,
    EquipmentResponse,
    IncreaseEquipmentStock,
)
from app.utils.enums import UserRole

router = APIRouter()

CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

ClubAdmin = Annotated[
    User,
    Depends(require_roles(UserRole.CLUB_ADMIN))
]

StudentOnly = Annotated[
    User,
    Depends(require_roles(UserRole.STUDENT))
]


def _get_current_student(db: DbSession, current_user: User) -> Student:
    """Resolve the Student profile linked to the authenticated user."""
    student = db.scalar(select(Student).where(Student.user_id == current_user.id))
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return student


def _equipment_response(equipment: Equipment) -> EquipmentResponse:
    """Build the equipment response from an equipment row."""
    return EquipmentResponse(
        id=equipment.id,
        name=equipment.name,
        category=equipment.category,
        description=equipment.description,
        total_quantity=equipment.total_quantity,
        available_quantity=equipment.available_quantity,
        storage_location=equipment.storage_location,
        equipment_image_url=equipment.equipment_image_url,
        created_at=equipment.created_at,
        updated_at=equipment.updated_at,
    )


def _borrow_detail_response(detail: BorrowDetail) -> BorrowDetailResponse:
    """Build the borrow detail response, including equipment and student names."""
    return BorrowDetailResponse(
        id=detail.id,
        equipment_id=detail.equipment_id,
        student_id=detail.student_id,
        borrowed_quantity=detail.borrowed_quantity,
        requested_date=detail.requested_date,
        return_date=detail.return_date,
        qr_code_url=detail.qr_code_url,
        created_at=detail.created_at,
        equipment_name=detail.equipment.name,
        student_name=detail.student.user.full_name,
        student_email=detail.student.user.email,
    )


# -------------------------------------------------------------- Equipment
@router.post(
    "/equipment",
    response_model=EquipmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_equipment(
    payload: EquipmentCreate,
    db: DbSession,
    current_user: ClubAdmin,
) -> Equipment:
    """Create a piece of equipment (club admin only)."""

    existing = db.scalar(select(Equipment).where(Equipment.name == payload.name))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Equipment with this name already exists",
        )
    
    if payload.available_quantity > payload.total_quantity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="available_quantity cannot exceed total_quantity",
        )
    

    equipment = Equipment(
        name=payload.name,
        category=payload.category,
        description=payload.description,
        total_quantity=payload.total_quantity,
        available_quantity=payload.available_quantity,
        storage_location=payload.storage_location,
        equipment_image_url=payload.equipment_image_url,
    )
    db.add(equipment)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create equipment",
        ) from exc
    db.refresh(equipment)
    return equipment


@router.post(
    "/equipment/stock/increase",
    response_model=EquipmentResponse,
)
def increase_equipment_stock(
    payload: IncreaseEquipmentStock,
    db: DbSession,
    current_user: ClubAdmin,
) -> Equipment:
    """Increase the stock of a piece of equipment (club admin only).

    ``increment_quantity`` is added to both ``total_quantity`` and
    ``available_quantity`` so the two stay in sync; the quantity in
    circulation is never affected.
    """
    equipment = db.scalar(select(Equipment).where(Equipment.id == payload.equipment_id))
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    equipment.total_quantity += payload.increment_quantity
    equipment.available_quantity += payload.increment_quantity

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to increase equipment stock",
        ) from exc
    db.refresh(equipment)
    return equipment


# ------------------------------------------------------------- Borrow detail
@router.post(
    "/equipment/borrow",
    response_model=BorrowDetailResponse,
)
def borrow_equipment(
    payload: BorrowEquipmentRequest,
    response: Response,
    db: DbSession,
    current_user: StudentOnly,
) -> BorrowDetailResponse:
    """Borrow a piece of equipment (student only).

    Each student may hold a single borrow detail per equipment; submitting
    another request for the same equipment increases the borrowed quantity and
    moves the return date instead of creating a duplicate row.
    """
    equipment = db.scalar(select(Equipment).where(Equipment.id == payload.equipment_id))
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    if payload.borrowed_quantity > equipment.available_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity exceeds available stock.",
        )

    student = _get_current_student(db, current_user)

    existing = db.scalar(
        select(BorrowDetail).where(
            BorrowDetail.equipment_id == equipment.id,
            BorrowDetail.student_id == student.id,
        )
    )

    if existing is not None:
        existing.borrowed_quantity += payload.borrowed_quantity
        existing.return_date = payload.return_date
        equipment.available_quantity -= payload.borrowed_quantity
        detail = existing
    else:
        detail = BorrowDetail(
            equipment_id=equipment.id,
            student_id=student.id,
            borrowed_quantity=payload.borrowed_quantity,
            requested_date=datetime.now(UTC),
            return_date=payload.return_date,
            qr_code_url=None,
        )
        db.add(detail)
        equipment.available_quantity -= payload.borrowed_quantity
        response.status_code = status.HTTP_201_CREATED

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to borrow equipment",
        ) from exc
    db.refresh(detail)
    return _borrow_detail_response(detail)


@router.delete(
    "/borrow-details/{borrow_detail_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_borrow_detail(
    borrow_detail_id: uuid.UUID,
    db: DbSession,
    current_user: ClubAdmin,
) -> None:
    """Return borrowed equipment to stock (club admin only).

    The quantity is released back into ``Equipment.available_quantity`` before
    the borrow record is deleted.
    """
    detail = db.scalar(
        select(BorrowDetail).where(BorrowDetail.id == borrow_detail_id)
    )
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow detail not found",
        )

    equipment = db.scalar(select(Equipment).where(Equipment.id == detail.equipment_id))
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    equipment.available_quantity += detail.borrowed_quantity
    db.delete(detail)

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete borrow detail",
        ) from exc