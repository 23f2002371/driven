# Student Club Management API

Production-ready backend for the Student Club Management Platform.

## Tech Stack

- Python 3.13+
- FastAPI
- SQLAlchemy 2.0 (Declarative ORM)
- Alembic (migrations)
- PostgreSQL (Supabase) via `psycopg[binary]`
- Pydantic v2 + pydantic-settings
- JWT auth (python-jose) + passlib[bcrypt]
- uv (dependency manager)

## Setup

```bash
cd backend
cp .env.example .env   # then fill in DATABASE_URL and SECRET_KEY
uv sync
```

## Run

```bash
uv run uvicorn app.main:app --reload
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## Database Migrations

```bash
# Generate a new migration after adding/editing models
uv run alembic revision --autogenerate -m "message"

# Apply migrations
uv run alembic upgrade head
```

## Seed Admin Accounts

After applying migrations, provision the two internal admin roles (club admin
and lab admin) with placeholder credentials:

```bash
uv run python -m app.services.seed
```

This creates:

| Role         | Email                    | Password    |
| ------------ | ------------------------ | ----------- |
| `club_admin` | `clubadmin@example.com`  | `Admin@1234` |
| `lab_admin`  | `labadmin@example.com`   | `Admin@1234` |

Change these placeholder credentials before going to production.

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── core/                # config, database, security
│   ├── api/                 # routers (per feature)
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # business logic
│   └── utils/               # helpers
├── alembic/                 # migrations
├── alembic.ini
├── pyproject.toml
└── .env.example
```

## Endpoints

| Method | Path              | Description                          |
| ------ | ----------------- | ------------------------------------ |
| GET    | `/`               | `{"message": "Student Club Management API"}` |
| GET    | `/api/health`     | `{"status": "healthy"}`              |
| POST   | `/api/auth/register` | Register a student account (role is always `student`) |
| POST   | `/api/auth/login` | Login, returns a JWT access token    |
| GET    | `/api/auth/me`    | Current user profile (Bearer token required) |
