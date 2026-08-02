from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.utils.enums import UserRole


class UserCreate(BaseModel):

    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=150)
    password: str = Field(min_length=8, max_length=255)


class UserLogin(BaseModel):

    email: EmailStr = Field(max_length=150)
    password: str = Field(min_length=1)


class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    role: UserRole
    created_at: datetime
