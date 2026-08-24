"""Inventory endpoints.

- ``GET    /equipment``                         - list all equipment.
- ``POST   /equipment``                         - create a piece of equipment (club admin only).
- ``POST   /equipment/stock/increase``          - increase stock of equipment (club admin only).
- ``POST   /equipment/borrow``                  - borrow equipment & generate QR pass (student only).
- ``GET    /equipment/borrow-details``          - list all borrow records (admin view).
- ``GET    /equipment/borrow-details/me``       - list current student's borrow records.
- ``POST   /equipment/borrow/verify``           - verify equipment borrow pass from QR/code (admin only).
- ``POST   /equipment/borrow/{id}/return``      - mark returned and restock (admin only).
- ``DELETE /borrow-details/{borrow_detail_id}`` - delete borrow detail & restore stock.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import String, cast, select

from app.api.deps import DbSession, get_current_user, require_roles
from app.core.config import settings
from app.models.inventory import BorrowDetail, Equipment
from app.models.student import Student
from app.models.user import User
from app.schemas.inventory import (
    BorrowDetailResponse,
    BorrowEquipmentRequest,
    EquipmentCreate,
    EquipmentResponse,
    IncreaseEquipmentStock,
    VerifyBorrowPassRequest,
    VerifyBorrowPassResponse,
)
from app.services.qr import extract_borrow_identifier, generate_borrow_qr_code
from app.utils.enums import EquipmentCategory, UserRole

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
    eq_category = None
    if detail.equipment:
        if hasattr(detail.equipment.category, "value"):
            eq_category = detail.equipment.category.value
        else:
            eq_category = str(detail.equipment.category)

    return BorrowDetailResponse(
        id=detail.id,
        equipment_id=detail.equipment_id,
        student_id=detail.student_id,
        borrowed_quantity=detail.borrowed_quantity,
        requested_date=detail.requested_date,
        return_date=detail.return_date,
        qr_code_url=detail.qr_code_url,
        created_at=detail.created_at,
        equipment_name=detail.equipment.name if detail.equipment else "Unknown Equipment",
        equipment_category=eq_category,
        equipment_image_url=detail.equipment.equipment_image_url if detail.equipment else None,
        storage_location=detail.equipment.storage_location if detail.equipment else None,
        student_name=detail.student.user.full_name if detail.student and detail.student.user else "Student",
        student_email=detail.student.user.email if detail.student and detail.student.user else "",
        student_roll_number=detail.student.student_id if detail.student else None,
    )


# -------------------------------------------------------------- Equipment
@router.get(
    "/equipment",
    response_model=list[EquipmentResponse],
)
def list_equipment(
    db: DbSession,
    current_user: CurrentUser,
) -> list[EquipmentResponse]:
    """List all equipment items in inventory."""
    items = db.scalars(
        select(Equipment).order_by(Equipment.created_at.desc())
    ).all()
    return [_equipment_response(eq) for eq in items]


@router.post(
    "/equipment",
    response_model=EquipmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_equipment(
    request: Request,
    db: DbSession,
    current_user: ClubAdmin,
) -> Equipment:
    """Create a piece of equipment (club admin only).
    
    Supports JSON and multipart/form-data with Cloudinary image upload.
    """
    content_type = request.headers.get("content-type", "")
    image_url: str | None = None

    if "multipart/form-data" in content_type:
        form = await request.form()
        name = str(form.get("name", "")).strip()
        raw_category = str(form.get("category", "")).strip()
        description_val = form.get("description")
        description = str(description_val).strip() if description_val else None

        try:
            total_quantity = int(form.get("total_quantity", 1))
        except (ValueError, TypeError):
            total_quantity = 1

        try:
            avail_val = form.get("available_quantity")
            available_quantity = int(avail_val) if avail_val is not None else total_quantity
        except (ValueError, TypeError):
            available_quantity = total_quantity

        storage_val = form.get("storage_location")
        storage_location = str(storage_val).strip() if storage_val else None

        direct_img = form.get("equipment_image_url") or form.get("image_url")
        if direct_img:
            image_url = str(direct_img).strip()

        image_file = form.get("equipment_image") or form.get("image") or form.get("cover_image")
        if image_file and hasattr(image_file, "file") and getattr(image_file, "filename", None):
            if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
                try:
                    import cloudinary
                    import cloudinary.uploader

                    cloudinary.config(
                        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                        api_key=settings.CLOUDINARY_API_KEY,
                        api_secret=settings.CLOUDINARY_API_SECRET,
                    )
                    file_bytes = await image_file.read()
                    if file_bytes:
                        upload_result = cloudinary.uploader.upload(
                            file_bytes,
                            folder="club-management/inventory",
                            resource_type="image",
                        )
                        image_url = upload_result.get("secure_url") or image_url
                except Exception:
                    pass
    else:
        body = await request.json()
        payload = EquipmentCreate.model_validate(body)
        name = payload.name.strip()
        raw_category = payload.category.value if isinstance(payload.category, EquipmentCategory) else str(payload.category).strip()
        description = payload.description.strip() if payload.description else None
        total_quantity = payload.total_quantity
        available_quantity = payload.available_quantity
        storage_location = payload.storage_location.strip() if payload.storage_location else None
        image_url = payload.equipment_image_url

    if not name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Equipment name is required",
        )
    if not raw_category:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Category is required",
        )

    # Normalize category enum
    cat_clean = raw_category.lower().replace(" ", "_").replace("-", "_").replace("/", "_")
    category_enum = None
    try:
        category_enum = EquipmentCategory(cat_clean)
    except ValueError:
        for member in EquipmentCategory:
            if member.value in cat_clean or cat_clean in member.value:
                category_enum = member
                break
        if category_enum is None:
            category_enum = EquipmentCategory.OTHER

    if total_quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="total_quantity must be at least 1",
        )
    if available_quantity > total_quantity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="available_quantity cannot exceed total_quantity",
        )

    existing = db.scalar(select(Equipment).where(Equipment.name == name))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Equipment with this name already exists",
        )

    equipment = Equipment(
        name=name,
        category=category_enum,
        description=description,
        total_quantity=total_quantity,
        available_quantity=available_quantity,
        storage_location=storage_location,
        equipment_image_url=image_url,
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
    """Increase the stock of a piece of equipment (club admin only)."""
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
    status_code=status.HTTP_201_CREATED,
)
def borrow_equipment(
    payload: BorrowEquipmentRequest,
    db: DbSession,
    current_user: StudentOnly,
) -> BorrowDetailResponse:
    """Borrow a piece of equipment & generate a QR borrow pass (student only).
    
    Requested date is now, return date deadline is 3 days later.
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
            detail=f"Requested quantity ({payload.borrowed_quantity}) exceeds available stock ({equipment.available_quantity}).",
        )

    student = _get_current_student(db, current_user)
    req_date = datetime.now(timezone.utc)
    ret_date = payload.return_date or (req_date + timedelta(days=3))

    borrow_id = uuid.uuid4()
    qr_code_url = generate_borrow_qr_code(
        borrow_id=borrow_id,
        equipment_id=equipment.id,
        student_id=student.id,
        api_prefix=settings.API_STR,
    )

    detail = BorrowDetail(
        id=borrow_id,
        equipment_id=equipment.id,
        student_id=student.id,
        borrowed_quantity=payload.borrowed_quantity,
        requested_date=req_date,
        return_date=ret_date,
        qr_code_url=qr_code_url,
    )
    db.add(detail)
    equipment.available_quantity -= payload.borrowed_quantity

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


@router.get(
    "/equipment/borrow-details",
    response_model=list[BorrowDetailResponse],
)
def list_borrow_details(
    db: DbSession,
    current_user: CurrentUser,
) -> list[BorrowDetailResponse]:
    """List all borrow records (club admin and lab admin view)."""
    details = db.scalars(
        select(BorrowDetail).order_by(BorrowDetail.created_at.desc())
    ).all()
    return [_borrow_detail_response(d) for d in details]


@router.get(
    "/equipment/borrow-details/me",
    response_model=list[BorrowDetailResponse],
)
def list_my_borrow_details(
    db: DbSession,
    current_user: StudentOnly,
) -> list[BorrowDetailResponse]:
    """List all borrow passes for the logged-in student."""
    student = _get_current_student(db, current_user)
    details = db.scalars(
        select(BorrowDetail)
        .where(BorrowDetail.student_id == student.id)
        .order_by(BorrowDetail.created_at.desc())
    ).all()
    return [_borrow_detail_response(d) for d in details]


@router.post(
    "/equipment/borrow/verify",
    response_model=VerifyBorrowPassResponse,
)
def verify_borrow_pass(
    payload: VerifyBorrowPassRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> VerifyBorrowPassResponse:
    """Verify an equipment borrow pass from QR code data or pass ID code."""
    input_str = payload.qr_code_data or payload.pass_id or (str(payload.borrow_id) if payload.borrow_id else "")
    if not input_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing QR code or Pass ID data",
        )

    parsed_uuid, short_prefix = extract_borrow_identifier(input_str)
    detail = None

    if parsed_uuid:
        detail = db.scalar(select(BorrowDetail).where(BorrowDetail.id == parsed_uuid))
    elif short_prefix:
        # Search by UUID prefix
        prefix_matches = db.scalars(
            select(BorrowDetail).where(
                cast(BorrowDetail.id, String).ilike(f"{short_prefix}%")
            )
        ).all()
        if prefix_matches:
            detail = prefix_matches[0]

    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment borrow pass not found for '{input_str}'.",
        )

    pass_code = f"BORROW-{str(detail.id)[:8].upper()}"
    now_utc = datetime.now(timezone.utc)
    is_overdue = detail.return_date < now_utc if detail.return_date else False

    eq_category = None
    if detail.equipment:
        if hasattr(detail.equipment.category, "value"):
            eq_category = detail.equipment.category.value
        else:
            eq_category = str(detail.equipment.category)

    return VerifyBorrowPassResponse(
        valid=True,
        message="Valid equipment borrow pass verified successfully.",
        borrow_id=detail.id,
        pass_id_code=pass_code,
        student_name=detail.student.user.full_name if detail.student and detail.student.user else "Student",
        student_email=detail.student.user.email if detail.student and detail.student.user else "",
        student_roll_number=detail.student.student_id if detail.student else None,
        equipment_name=detail.equipment.name if detail.equipment else "Equipment",
        equipment_category=eq_category,
        equipment_image_url=detail.equipment.equipment_image_url if detail.equipment else None,
        storage_location=detail.equipment.storage_location if detail.equipment else None,
        borrowed_quantity=detail.borrowed_quantity,
        requested_date=detail.requested_date,
        return_date=detail.return_date,
        qr_code_url=detail.qr_code_url,
        is_overdue=is_overdue,
    )


@router.post(
    "/equipment/borrow/{borrow_id}/return",
    response_model=dict[str, Any],
)
def return_borrowed_equipment(
    borrow_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Mark borrowed equipment as returned and restock available quantity."""
    detail = db.scalar(select(BorrowDetail).where(BorrowDetail.id == borrow_id))
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow record not found",
        )

    equipment = db.scalar(select(Equipment).where(Equipment.id == detail.equipment_id))
    if equipment:
        equipment.available_quantity = min(equipment.total_quantity, equipment.available_quantity + detail.borrowed_quantity)

    qty_returned = detail.borrowed_quantity
    eq_name = equipment.name if equipment else "Equipment"
    new_avail = equipment.available_quantity if equipment else 0
    db.delete(detail)

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process equipment return",
        ) from exc

    return {
        "success": True,
        "message": f"Successfully returned {qty_returned} units of '{eq_name}'. Stock restored to {new_avail}.",
        "equipment_id": str(equipment.id) if equipment else None,
        "available_quantity": new_avail,
    }


@router.delete(
    "/borrow-details/{borrow_detail_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_borrow_detail(
    borrow_detail_id: uuid.UUID,
    db: DbSession,
    current_user: ClubAdmin,
) -> None:
    """Return borrowed equipment to stock (club admin only)."""
    detail = db.scalar(
        select(BorrowDetail).where(BorrowDetail.id == borrow_detail_id)
    )
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow detail not found",
        )

    equipment = db.scalar(select(Equipment).where(Equipment.id == detail.equipment_id))
    if equipment:
        equipment.available_quantity = min(equipment.total_quantity, equipment.available_quantity + detail.borrowed_quantity)

    db.delete(detail)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete borrow detail",
        ) from exc