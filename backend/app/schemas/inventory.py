"""Pydantic schemas for the Inventory domain."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------- Equipment
class EquipmentCreate(BaseModel):
    """Payload to create a piece of equipment."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=150)
    category: str = Field(min_length=1, max_length=100)
    description: str | None = None
    total_quantity: int = Field(ge=1)
    available_quantity: int = Field(ge=0)
    storage_location: str | None = Field(default=None, max_length=150)
    equipment_image_url: str | None = None


class EquipmentUpdate(BaseModel):
    """Payload to update a piece of equipment. Every field is optional."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=150)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    storage_location: str | None = Field(default=None, max_length=150)
    equipment_image_url: str | None = None


class IncreaseEquipmentStock(BaseModel):
    """Payload to increase the stock of a piece of equipment."""

    model_config = ConfigDict(extra="forbid")

    equipment_id: UUID
    increment_quantity: int = Field(ge=1)


class EquipmentResponse(BaseModel):
    """Representation of a piece of equipment."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    category: str
    description: str | None
    total_quantity: int
    available_quantity: int
    storage_location: str | None
    equipment_image_url: str | None
    created_at: datetime
    updated_at: datetime


# ----------------------------------------------------------- Borrow detail
class BorrowEquipmentRequest(BaseModel):
    """Payload to borrow a piece of equipment."""

    model_config = ConfigDict(extra="forbid")

    equipment_id: UUID
    borrowed_quantity: int = Field(ge=1)
    return_date: datetime


class BorrowDetailResponse(BaseModel):
    """Representation of a borrow detail entry.

    ``equipment_name`` and ``student_name`` are resolved from the related
    equipment and student and are therefore built by a helper rather than
    loaded directly from the borrow detail row.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    equipment_id: UUID
    student_id: UUID
    borrowed_quantity: int
    requested_date: datetime
    return_date: datetime
    qr_code_url: str | None
    created_at: datetime
    equipment_name: str
    student_name: str
    student_email: str