"""Pydantic schemas for the Student model.

Profile-only: ``user_id`` is never part of a request/response payload, it is
derived from the authenticated user server-side.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import Department, Skill


class StudentCreate(BaseModel):

    student_id: str = Field(min_length=1, max_length=20)
    department: Department
    phone: str | None = Field(default=None, max_length=20)
    github_username: str | None = Field(default=None, max_length=100)
    linkedin_username: str | None = Field(default=None, max_length=100)
    portfolio_url: str | None = Field(default=None, max_length=255)


class StudentUpdate(BaseModel):

    student_id: str | None = Field(default=None, min_length=1, max_length=20)
    department: Department | None = None
    phone: str | None = Field(default=None, max_length=20)
    github_username: str | None = Field(default=None, max_length=100)
    linkedin_username: str | None = Field(default=None, max_length=100)
    portfolio_url: str | None = Field(default=None, max_length=255)


class StudentResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: str
    user_id: UUID
    user_full_name: str
    user_email: str
    department: Department
    phone: str | None
    github_username: str | None
    linkedin_username: str | None
    portfolio_url: str | None
    skills: list[StudentSkillResponse] = []
    created_at: datetime
    updated_at: datetime


class StudentSkillCreate(BaseModel):

    skill: Skill


class StudentSkillUpdate(BaseModel):

    skill: Skill | None = None


class StudentSkillResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    skill: Skill
