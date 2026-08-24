"""AI endpoints for Agentic Copilot, Event Generation, and Smart Bounty Match Analysis."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import DbSession, require_roles
from app.core.config import settings
from app.models.user import User
from app.utils.enums import UserRole

router = APIRouter(prefix="/ai", tags=["ai"])

AdminUser = Annotated[User, Depends(require_roles(UserRole.CLUB_ADMIN, UserRole.LAB_ADMIN))]
ClubAdminOnly = Annotated[User, Depends(require_roles(UserRole.CLUB_ADMIN))]


class CopilotRequest(BaseModel):
    prompt: str


class EventGenRequest(BaseModel):
    prompt: str


class GeneratedEvent(BaseModel):
    name: str = Field(description="The name of the event")
    short_description: str = Field(description="A brief one-line description")
    category: str = Field(description="One of: workshop, hackathon, seminar, competition, bootcamp, webinar, robotics, other")
    event_date: str = Field(description="Date in YYYY-MM-DD format")
    registration_deadline: str = Field(description="Datetime in ISO format (YYYY-MM-DDTHH:MM:SSZ)")
    venue: str = Field(description="One of: seminar_hall, auditorium, main_ground, computer_lab_1, computer_lab_2, robotics_lab, innovation_lab, conference_room, classroom, online, other")
    max_participants: int = Field(description="Maximum number of participants allowed")
    description: str = Field(description="Detailed description of the event")


class MatchAnalysisResponse(BaseModel):
    match_score: int = Field(description="A score from 0 to 100 indicating fit")
    summary: str = Field(description="A concise 2-sentence summary of the candidate's suitability.")


@router.post("/copilot")
def copilot_chat(
    payload: CopilotRequest,
    db: DbSession,
    current_user: AdminUser,
):
    """Context-aware agentic copilot resolving multi-step logistics and club queries."""
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini API Key missing in environment settings.",
        )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        def check_inventory(equipment_name: str) -> str:
            """Searches inventory for equipment by name and returns availability."""
            from app.models.inventory import Equipment

            eq = db.scalar(
                select(Equipment).where(Equipment.name.ilike(f"%{equipment_name}%"))
            )
            return (
                f"Found {eq.name}: {eq.available_quantity} available out of {eq.total_quantity}."
                if eq
                else f"Equipment '{equipment_name}' not found."
            )

        def get_upcoming_events() -> str:
            """Returns the names, dates, and venues of upcoming events."""
            from app.models.event import Event

            events = list(db.scalars(select(Event).limit(5)))
            return (
                "\n".join(
                    [
                        f"{e.name} on {e.event_date} at {e.venue.value if hasattr(e.venue, 'value') else e.venue}"
                        for e in events
                    ]
                )
                if events
                else "No upcoming events found."
            )

        def search_roster(query: str = "") -> str:
            """Searches student roster, members, and leads by name, department, or student ID."""
            from app.models.student import Student
            from app.models.user import User

            if query:
                students = list(
                    db.scalars(
                        select(Student)
                        .join(User, Student.user_id == User.id)
                        .where(
                            (User.full_name.ilike(f"%{query}%"))
                            | (Student.department.ilike(f"%{query}%"))
                            | (Student.student_id.ilike(f"%{query}%"))
                        )
                        .limit(10)
                    )
                )
            else:
                students = list(db.scalars(select(Student).limit(10)))

            if not students:
                return f"No students found matching '{query}'." if query else "No students registered."
            return "\n".join(
                [
                    f"- {s.user.full_name if s.user else 'Student'} ({s.student_id}) · {s.department}"
                    for s in students
                ]
            )

        def get_bounties_summary() -> str:
            """Fetches active campus bounties, domains, and available student seats."""
            from app.models.bounty import Bounty

            bounties = list(db.scalars(select(Bounty).limit(10)))
            if not bounties:
                return "No campus bounties found."
            return "\n".join(
                [
                    f"- {b.title} (Domain: {b.domain.name.value if hasattr(b.domain.name, 'value') else b.domain.name}) | Reward: ₹{b.reward} | Seats: {b.student_seats} | Status: {b.status.value if hasattr(b.status, 'value') else b.status}"
                    for b in bounties
                ]
            )

        chat = client.chats.create(
            model="gemini-3.6-flash",
            config=types.GenerateContentConfig(
                tools=[check_inventory, get_upcoming_events, search_roster, get_bounties_summary],
                temperature=0.2,
                system_instruction=(
                    "You are DRIVEN Copilot, an AI assistant for a student club management platform. "
                    "You have direct access to database tools: check_inventory, get_upcoming_events, search_roster, and get_bounties_summary. "
                    "Use these tools to query real data when answering questions about equipment availability, upcoming events, student members, or bounties. "
                    "Provide clear, concise, and helpful answers."
                ),
            ),
        )

        response = chat.send_message(payload.prompt)
        return {"text": response.text}
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Copilot error: {exc}",
        ) from exc


@router.post("/events/generate", response_model=GeneratedEvent)
def generate_event(
    payload: EventGenRequest,
    current_user: ClubAdminOnly,
):
    """Natural language event detail extraction into structured database schema."""
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini API Key missing in environment settings.",
        )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"Extract event details from this request: {payload.prompt}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeneratedEvent,
                temperature=0.2,
            ),
        )
        return response.parsed
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event generation error: {exc}",
        ) from exc


@router.get("/applications/{application_id}/analyze", response_model=MatchAnalysisResponse)
def analyze_application(
    application_id: uuid.UUID,
    db: DbSession,
    current_user: ClubAdminOnly,
):
    """Evaluate student bounty application fit against bounty requirements."""
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini API Key missing in environment settings.",
        )

    from app.models.bounty import Application
    from sqlalchemy.orm import selectinload

    app_record = db.scalar(
        select(Application)
        .where(Application.id == application_id)
        .options(
            selectinload(Application.bounty),
            selectinload(Application.student),
        )
    )
    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    prompt = (
        f"Bounty: {app_record.bounty.title}\n"
        f"Description: {app_record.bounty.description}\n"
        f"Student Department: {app_record.student.department if app_record.student else 'N/A'}\n"
        f"Student Availability: {app_record.availability}\n"
        f"Resume/Portfolio: {app_record.resume or 'None'}\n"
        f"Evaluate how well this student fits the bounty requirements and produce a match score (0-100) and concise 2-sentence summary."
    )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MatchAnalysisResponse,
                temperature=0.2,
            ),
        )
        return response.parsed
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Match analysis error: {exc}",
        ) from exc
