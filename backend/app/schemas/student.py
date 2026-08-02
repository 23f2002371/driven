"""Pydantic schemas for the Student model.

Profile-only: ``user_id`` is never part of a request/response payload, it is
derived from the authenticated user server-side.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StudentCreate(BaseModel):

    phone: str | None = Field(default=None, max_length=20)
    github_username: str | None = Field(default=None, max_length=100)
    linkedin_username: str | None = Field(default=None, max_length=100)
    portfolio_url: str | None = Field(default=None, max_length=255)


class StudentUpdate(BaseModel):

    phone: str | None = Field(default=None, max_length=20)
    github_username: str | None = Field(default=None, max_length=100)
    linkedin_username: str | None = Field(default=None, max_length=100)
    portfolio_url: str | None = Field(default=None, max_length=255)


class StudentResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phone: str | None
    github_username: str | None
    linkedin_username: str | None
    portfolio_url: str | None
    created_at: datetime
    updated_at: datetime
