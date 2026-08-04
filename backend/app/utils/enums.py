"""Application enums.

Enums are defined here so they can be shared between the SQLAlchemy models
(database layer) and the Pydantic schemas (API layer).

Each enum subclasses ``str`` so that serialized values match the PostgreSQL
enum values exactly.
"""

from enum import Enum


class UserRole(str, Enum):
    """Role assigned to a user.

    Only ``STUDENT`` is reachable through the public API. The administrative
    roles are created internally via seeding or future admin tooling.
    """

    STUDENT = "student"
    CLUB_ADMIN = "club_admin"
    LAB_ADMIN = "lab_admin"


class EventCategory(str, Enum):
    """Top-level category of an event."""

    WORKSHOP = "workshop"
    HACKATHON = "hackathon"
    SEMINAR = "seminar"
    COMPETITION = "competition"
    BOOTCAMP = "bootcamp"
    WEBINAR = "webinar"
    ROBOTICS = "robotics"
    OTHER = "other"


class EventStatus(str, Enum):
    """Approval state of an event.

    New events are created as ``pending`` until a club/lab admin approves or
    rejects them.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AdditionalInfoType(str, Enum):
    """Type of an extra event information section."""

    LEARNING = "learning"
    REQUIREMENT = "requirement"
    ELIGIBILITY = "eligibility"


class RegistrationStatus(str, Enum):
    """Registration state of a student for an event."""

    PENDING = "pending"
    REGISTERED = "registered"


class AttendanceStatus(str, Enum):
    """Attendance state of a registered student."""

    ABSENT = "absent"
    PRESENT = "present"


class WinnerPosition(str, Enum):
    """Podium position of an event winner."""

    FIRST = "first"
    SECOND = "second"
    THIRD = "third"


class Department(str, Enum):
    """Academic department of a student."""

    COMPUTER_SCIENCE = "computer_science"
    INFORMATION_TECHNOLOGY = "information_technology"
    ELECTRONICS = "electronics"
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    CIVIL = "civil"
    CHEMICAL = "chemical"
    BIOTECHNOLOGY = "biotechnology"
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    OTHER = "other"


class Skill(str, Enum):
    """A skill a student can declare."""

    WEB_DEVELOPMENT = "web_development"
    APP_DEVELOPMENT = "app_development"
    AI_ML = "ai_ml"
    DATA_SCIENCE = "data_science"
    CYBER_SECURITY = "cyber_security"
    CLOUD_COMPUTING = "cloud_computing"
    DEVOPS = "devops"
    UI_UX_DESIGN = "ui_ux_design"
    ROBOTICS = "robotics"
    IOT = "iot"
    COMPETITIVE_PROGRAMMING = "competitive_programming"
    BLOCKCHAIN = "blockchain"
    GAME_DEVELOPMENT = "game_development"
    OTHER = "other"


class EventVenue(str, Enum):
    """Where an event takes place."""

    SEMINAR_HALL = "seminar_hall"
    AUDITORIUM = "auditorium"
    MAIN_GROUND = "main_ground"
    COMPUTER_LAB_1 = "computer_lab_1"
    COMPUTER_LAB_2 = "computer_lab_2"
    ROBOTICS_LAB = "robotics_lab"
    INNOVATION_LAB = "innovation_lab"
    CONFERENCE_ROOM = "conference_room"
    CLASSROOM = "classroom"
    ONLINE = "online"
    OTHER = "other"
