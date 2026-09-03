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


class GeneratedAgenda(BaseModel):
    start_time: str = Field(description="Start time in HH:MM format (24-hour), e.g. '09:00'")
    end_time: str = Field(description="End time in HH:MM format (24-hour), e.g. '10:30'")
    title: str = Field(description="Session or slot title, e.g. 'Keynote & Architecture Overview'")
    description: str = Field(description="Brief outline of topics, demos, or activities in this slot")


class GeneratedAdditionalInfo(BaseModel):
    section_type: str = Field(description="Must be one of: learning, requirement, eligibility")
    content: str = Field(description="Bullet point content for the section")


class GeneratedEvent(BaseModel):
    name: str = Field(description="The name of the event")
    short_description: str = Field(description="A brief one-line description (max 255 characters)")
    category: str = Field(description="One of: workshop, hackathon, seminar, competition, bootcamp, webinar, robotics, other")
    event_date: str = Field(description="Date in YYYY-MM-DD format")
    registration_deadline: str = Field(description="Datetime in ISO format (YYYY-MM-DDTHH:MM:SSZ)")
    venue: str = Field(description="One of: seminar_hall, auditorium, main_ground, computer_lab_1, computer_lab_2, robotics_lab, innovation_lab, conference_room, classroom, online, other")
    max_participants: int = Field(description="Maximum number of participants allowed")
    description: str = Field(description="Detailed description of the event")
    agendas: list[GeneratedAgenda] = Field(default_factory=list, description="2 to 4 realistic time-slots for this event")
    additional_info: list[GeneratedAdditionalInfo] = Field(
        default_factory=list,
        description="Key bullet points with section_type 'learning' (Learning Outcomes), 'requirement' (Prerequisites & Requirements), and 'eligibility' (Eligibility Details)"
    )


class SuggestDetailsRequest(BaseModel):
    name: str
    category: str = "workshop"
    description: str = ""
    short_description: str = ""
    venue: str = ""
    event_date: str = ""


class SuggestedDetailsResponse(BaseModel):
    agendas: list[GeneratedAgenda] = Field(default_factory=list, description="2 to 4 realistic time-slots for this event")
    additional_info: list[GeneratedAdditionalInfo] = Field(
        default_factory=list,
        description="Structured bullet points with section_type 'learning', 'requirement', and 'eligibility'"
    )


class MatchAnalysisResponse(BaseModel):
    match_score: int = Field(description="A score from 0 to 100 indicating fit")
    summary: str = Field(description="A concise 2-sentence summary of the candidate's suitability.")


FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


def generate_content_with_fallback(client, contents, config, models: list[str] | None = None):
    """Attempt content generation across multiple Gemini models if one model fails or is busy."""
    models_to_try = models or FALLBACK_MODELS
    last_error = None

    for model_name in models_to_try:
        try:
            return client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
        except Exception as exc:
            last_error = exc
            # Try next model in sequence
            continue

    if last_error:
        raise last_error


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

        chat_config = types.GenerateContentConfig(
            tools=[check_inventory, get_upcoming_events, search_roster, get_bounties_summary],
            temperature=0.2,
            system_instruction=(
                "You are DRIVEN Copilot, an AI assistant for a student club management platform. "
                "You have direct access to database tools: check_inventory, get_upcoming_events, search_roster, and get_bounties_summary. "
                "Use these tools to query real data when answering questions about equipment availability, upcoming events, student members, or bounties. "
                "Provide clear, concise, and helpful answers."
            ),
        )

        last_err = None
        for model_candidate in FALLBACK_MODELS:
            try:
                chat = client.chats.create(
                    model=model_candidate,
                    config=chat_config,
                )
                response = chat.send_message(payload.prompt)
                return {"text": response.text}
            except Exception as e:
                last_err = e
                err_str = str(e)
                if any(k in err_str for k in ("503", "UNAVAILABLE", "429", "demand", "NotFound", "RESOURCE_EXHAUSTED")):
                    continue
                raise e

        if last_err:
            raise last_err
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
    """Natural language event detail extraction into structured database schema including agendas and additional info."""
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini API Key missing in environment settings.",
        )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        system_instruction = (
            "You are an expert event planning assistant for a college student club. "
            "Extract or intelligently generate comprehensive event details based on the user's prompt. "
            "In addition to basic details, generate: "
            "1. Realistic agendas: 2 to 4 chronological time-slots (start_time e.g. '09:00', end_time e.g. '10:30', session title, and concise description). "
            "2. Additional info bullet points with section_type: "
            "   - 'learning': 2 to 4 key learning outcomes students will gain. "
            "   - 'requirement': 2 to 3 prerequisites, software, hardware, or tools needed. "
            "   - 'eligibility': 1 to 2 eligibility criteria (e.g. eligible branches, study years, team sizes)."
        )
        response = generate_content_with_fallback(
            client=client,
            contents=f"Extract and generate complete event details, agendas, learning outcomes, requirements, and eligibility for this request: {payload.prompt}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeneratedEvent,
                temperature=0.2,
                system_instruction=system_instruction,
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


@router.post("/events/suggest-details", response_model=SuggestedDetailsResponse)
def suggest_event_details(
    payload: SuggestDetailsRequest,
    current_user: ClubAdminOnly,
):
    """Generate tailored agendas, learning outcomes, prerequisites, and eligibility based on existing event info."""
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini API Key missing in environment settings.",
        )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        context = (
            f"Event Name: {payload.name}\n"
            f"Category: {payload.category}\n"
            f"Short Description: {payload.short_description}\n"
            f"Description: {payload.description}\n"
            f"Venue: {payload.venue}\n"
            f"Date: {payload.event_date}\n"
        )
        system_instruction = (
            "You are an expert college event planner. Based on the provided event details, generate: "
            "1. Agendas: 2 to 4 chronological agenda slots with realistic start_time (HH:MM in 24-hour format), end_time (HH:MM in 24-hour format), session title, and description. "
            "2. Additional Info: "
            "   - section_type 'learning': 2 to 4 clear learning outcomes. "
            "   - section_type 'requirement': 2 to 3 prerequisites, required software, or hardware. "
            "   - section_type 'eligibility': 1 to 2 eligibility rules (branch, year, teams)."
        )
        response = generate_content_with_fallback(
            client=client,
            contents=f"Generate tailored schedule agendas, learning outcomes, requirements/prerequisites, and eligibility details for this event:\n{context}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SuggestedDetailsResponse,
                temperature=0.2,
                system_instruction=system_instruction,
            ),
        )
        return response.parsed
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Suggest details error: {exc}",
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
        response = generate_content_with_fallback(
            client=client,
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
