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


class CertificateType(str, Enum):
    """Kind of certificate issued for an event registration."""

    PARTICIPATION = "participation"
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


class DomainEnum(str, Enum):
    """A skill domain a student can declare."""

    PROGRAMMING_LANGUAGES = "PROGRAMMING_LANGUAGES"
    WEB_DEVELOPMENT = "WEB_DEVELOPMENT"
    BACKEND_DEVELOPMENT = "BACKEND_DEVELOPMENT"
    APP_DEVELOPMENT = "APP_DEVELOPMENT"
    AI_ML = "AI_ML"
    DATA_SCIENCE = "DATA_SCIENCE"
    CYBER_SECURITY = "CYBER_SECURITY"
    CLOUD_COMPUTING = "CLOUD_COMPUTING"
    DEVOPS = "DEVOPS"
    DATABASE = "DATABASE"
    UI_UX_DESIGN = "UI_UX_DESIGN"
    ROBOTICS = "ROBOTICS"
    IOT = "IOT"
    BLOCKCHAIN = "BLOCKCHAIN"
    GAME_DEVELOPMENT = "GAME_DEVELOPMENT"
    COMPETITIVE_PROGRAMMING = "COMPETITIVE_PROGRAMMING"


class TechnologyEnum(str, Enum):
    """A technology a student can declare within a domain."""

    # Programming Languages
    PYTHON = "PYTHON"
    JAVA = "JAVA"
    C = "C"
    CPP = "CPP"
    C_SHARP = "C_SHARP"
    JAVASCRIPT = "JAVASCRIPT"
    TYPESCRIPT = "TYPESCRIPT"
    GO = "GO"
    RUST = "RUST"
    PHP = "PHP"
    KOTLIN = "KOTLIN"
    SWIFT = "SWIFT"
    DART = "DART"
    R = "R"

    # Web Development
    HTML = "HTML"
    CSS = "CSS"
    TAILWIND_CSS = "TAILWIND_CSS"
    BOOTSTRAP = "BOOTSTRAP"
    REACT = "REACT"
    NEXT_JS = "NEXT_JS"
    VUE_JS = "VUE_JS"
    NUXT_JS = "NUXT_JS"
    ANGULAR = "ANGULAR"
    SVELTE = "SVELTE"

    # Backend Development
    NODE_JS = "NODE_JS"
    EXPRESS_JS = "EXPRESS_JS"
    FASTAPI = "FASTAPI"
    FLASK = "FLASK"
    DJANGO = "DJANGO"
    SPRING_BOOT = "SPRING_BOOT"
    NEST_JS = "NEST_JS"
    LARAVEL = "LARAVEL"
    ASP_NET = "ASP_NET"
    GRAPHQL = "GRAPHQL"
    REST_API = "REST_API"

    # App Development
    FLUTTER = "FLUTTER"
    REACT_NATIVE = "REACT_NATIVE"
    ANDROID = "ANDROID"
    JETPACK_COMPOSE = "JETPACK_COMPOSE"
    SWIFT_UI = "SWIFT_UI"

    # AI / ML
    NUMPY = "NUMPY"
    PANDAS = "PANDAS"
    SCIKIT_LEARN = "SCIKIT_LEARN"
    TENSORFLOW = "TENSORFLOW"
    PYTORCH = "PYTORCH"
    KERAS = "KERAS"
    OPENCV = "OPENCV"
    LANGCHAIN = "LANGCHAIN"
    HUGGING_FACE = "HUGGING_FACE"
    OPENAI_API = "OPENAI_API"

    # Data Science
    MATPLOTLIB = "MATPLOTLIB"
    SEABORN = "SEABORN"
    POWER_BI = "POWER_BI"
    TABLEAU = "TABLEAU"
    JUPYTER = "JUPYTER"

    # Cyber Security
    KALI_LINUX = "KALI_LINUX"
    WIRESHARK = "WIRESHARK"
    BURP_SUITE = "BURP_SUITE"
    NMAP = "NMAP"
    METASPLOIT = "METASPLOIT"
    OWASP = "OWASP"

    # Cloud Computing
    AWS = "AWS"
    AZURE = "AZURE"
    GOOGLE_CLOUD = "GOOGLE_CLOUD"
    FIREBASE = "FIREBASE"
    SUPABASE = "SUPABASE"

    # DevOps
    DOCKER = "DOCKER"
    KUBERNETES = "KUBERNETES"
    JENKINS = "JENKINS"
    GITHUB_ACTIONS = "GITHUB_ACTIONS"
    TERRAFORM = "TERRAFORM"
    ANSIBLE = "ANSIBLE"
    NGINX = "NGINX"
    LINUX = "LINUX"

    # Database
    POSTGRESQL = "POSTGRESQL"
    MYSQL = "MYSQL"
    SQLITE = "SQLITE"
    MONGODB = "MONGODB"
    REDIS = "REDIS"
    ORACLE = "ORACLE"
    SQL_SERVER = "SQL_SERVER"

    # UI / UX
    FIGMA = "FIGMA"
    ADOBE_XD = "ADOBE_XD"
    CANVA = "CANVA"
    PHOTOSHOP = "PHOTOSHOP"
    ILLUSTRATOR = "ILLUSTRATOR"

    # Robotics
    ROS = "ROS"
    ARDUINO = "ARDUINO"
    RASPBERRY_PI = "RASPBERRY_PI"

    # IoT
    ESP32 = "ESP32"
    MQTT = "MQTT"

    # Blockchain
    SOLIDITY = "SOLIDITY"
    HARDHAT = "HARDHAT"
    FOUNDRY = "FOUNDRY"
    ETHERS_JS = "ETHERS_JS"
    WEB3_JS = "WEB3_JS"

    # Game Development
    UNITY = "UNITY"
    UNREAL_ENGINE = "UNREAL_ENGINE"
    GODOT = "GODOT"
    BLENDER = "BLENDER"

    # Competitive Programming
    CODEFORCES = "CODEFORCES"
    CODECHEF = "CODECHEF"
    LEETCODE = "LEETCODE"
    ATCODER = "ATCODER"
    HACKERRANK = "HACKERRANK"


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

class BountyStatus(str, Enum):
    """Lifecycle state of a campus bounty."""

    OPEN = "open"
    CLOSED = "closed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ApplicationStatus(str, Enum):
    """State of a student's application to a bounty.

    Students cannot withdraw; an application that is not ``accepted`` is
    ultimately ``rejected``.
    """

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class WorkStatus(str, Enum):
    """Progress state of work assigned to an accepted student.

    Acceptance is modelled by :class:`ApplicationStatus`; a ``Work`` record is
    only created for an accepted application.
    """

    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class DeliverableStatus(str, Enum):
    """Progress state of a deliverable attached to a work record."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"