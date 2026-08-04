"""Generate the API test matrix markdown document.

Builds ``tests/test-cases/api-test-matrix.md`` from the tests that are
actually implemented in the suite. Endpoints with no corresponding test are
excluded. If ``tests/reports/results_log.json`` exists (written by each pytest
run), the ``Actual Output`` and ``Result`` columns reflect the latest run;
otherwise they show the expected outcome only.

Usage::

    uv run python -m tests.tools.generate_test_matrix
"""

from __future__ import annotations

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = BASE_DIR / "test-cases" / "api-test-matrix.md"
RESULTS_LOG = BASE_DIR / "reports" / "results_log.json"


def _out(*lines: str) -> str:
    """Build a multi-line cell body from the given lines."""
    return "<br>".join(lines)


# Metadata for every implemented test. Only tests present in this registry
# (and actually defined in a test file) are listed in the matrix.
TESTS: dict[str, dict[str, str]] = {
    "test_register_success": {
        "id": "AUTH-001",
        "description": "Register a valid student account",
        "api": "POST /api/auth/register",
        "inputs": "full_name='Jane Doe'<br>email='jane@example.com'<br>password='securepass123'",
        "expected": _out(
            "Status: 201 Created",
            "full_name: 'Jane Doe'",
            "email: 'jane@example.com'",
            "role: 'student'",
            "Message: user created successfully",
        ),
    },
    "test_register_duplicate_email": {
        "id": "AUTH-002",
        "description": "Register with an already used email",
        "api": "POST /api/auth/register",
        "inputs": "email='dup@example.com' (already registered)",
        "expected": _out(
            "Status: 409 Conflict",
            "Message: an account with this email already exists",
        ),
    },
    "test_register_invalid_email": {
        "id": "AUTH-003",
        "description": "Register with a malformed email",
        "api": "POST /api/auth/register",
        "inputs": "email='not-an-email'",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "Message: email is not a valid email address",
        ),
    },
    "test_register_missing_required_field": {
        "id": "AUTH-004",
        "description": "Register without a required field",
        "api": "POST /api/auth/register",
        "inputs": "email='jane@example.com'<br>password='securepass123' (no full_name)",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "Message: full_name field required",
        ),
    },
    "test_register_short_password": {
        "id": "AUTH-005",
        "description": "Register with a password shorter than 8 chars",
        "api": "POST /api/auth/register",
        "inputs": "password='short'",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "Message: password must be at least 8 characters",
        ),
    },
    "test_register_missing_credentials_variants": {
        "id": "AUTH-006",
        "description": "Register with missing fields (parametrized)",
        "api": "POST /api/auth/register",
        "inputs": "{}, email only, password only",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "Message: one or more required fields missing",
        ),
    },
    "test_login_success": {
        "id": "AUTH-007",
        "description": "Login with valid credentials",
        "api": "POST /api/auth/login",
        "inputs": "email='jane@example.com'<br>password='securepass123'",
        "expected": _out(
            "Status: 200 OK",
            "access_token: <jwt token>",
            "token_type: 'bearer'",
        ),
    },
    "test_login_wrong_password": {
        "id": "AUTH-008",
        "description": "Login with an incorrect password",
        "api": "POST /api/auth/login",
        "inputs": "email='jane@example.com'<br>password='wrongpass123'",
        "expected": _out(
            "Status: 401 Unauthorized",
            "Message: incorrect email or password",
        ),
    },
    "test_login_unknown_email": {
        "id": "AUTH-009",
        "description": "Login with an unregistered email",
        "api": "POST /api/auth/login",
        "inputs": "email='ghost@example.com'<br>password='securepass123'",
        "expected": _out(
            "Status: 401 Unauthorized",
            "Message: incorrect email or password",
        ),
    },
    "test_login_oauth_only_user": {
        "id": "AUTH-010",
        "description": "Login for an OAuth-only user with no password",
        "api": "POST /api/auth/login",
        "inputs": "email='oauth@example.com'<br>password='anything'",
        "expected": _out(
            "Status: 401 Unauthorized",
            "Message: incorrect email or password",
        ),
    },
    "test_login_missing_credentials": {
        "id": "AUTH-011",
        "description": "Login with an empty body",
        "api": "POST /api/auth/login",
        "inputs": "{}",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "Message: one or more required fields missing",
        ),
    },
    "test_create_event_as_club_admin": {
        "id": "EVENT-001",
        "description": "Club admin creates an event",
        "api": "POST /api/events",
        "inputs": "valid EventCreate payload (status not set)",
        "expected": _out(
            "Status: 201 Created",
            "name: 'Intro to AI Workshop'",
            "status: 'pending'",
            "Message: event created successfully",
        ),
    },
    "test_create_event_as_student_forbidden": {
        "id": "EVENT-002",
        "description": "Student tries to create an event",
        "api": "POST /api/events",
        "inputs": "valid EventCreate payload",
        "expected": _out(
            "Status: 403 Forbidden",
            "Message: insufficient permissions",
        ),
    },
    "test_create_event_invalid_payload": {
        "id": "EVENT-003",
        "description": "Create event with max_participants=0",
        "api": "POST /api/events",
        "inputs": "valid payload<br>max_participants=0",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "Message: max_participants must be >= 1",
        ),
    },
    "test_create_event_missing_required_field": {
        "id": "EVENT-004",
        "description": "Create event without description",
        "api": "POST /api/events",
        "inputs": "valid payload minus description",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "Message: description field required",
        ),
    },
    "test_create_event_unauthenticated": {
        "id": "EVENT-005",
        "description": "Create event without a token",
        "api": "POST /api/events",
        "inputs": "valid EventCreate payload, no auth header",
        "expected": _out(
            "Status: 401 Unauthorized",
            "Message: could not validate credentials",
        ),
    },
    "test_get_event_success": {
        "id": "EVENT-006",
        "description": "Fetch an existing event",
        "api": "GET /api/events/{event_id}",
        "inputs": "valid event id, no auth",
        "expected": _out(
            "Status: 200 OK",
            "id: <event id>",
            "name: 'Existing Event'",
        ),
    },
    "test_get_event_invalid_uuid": {
        "id": "EVENT-007",
        "description": "Fetch event with a malformed id",
        "api": "GET /api/events/{event_id}",
        "inputs": "'not-a-uuid'",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "Message: event_id is not a valid UUID",
        ),
    },
    "test_get_event_not_found": {
        "id": "EVENT-008",
        "description": "Fetch a non-existent event",
        "api": "GET /api/events/{event_id}",
        "inputs": "00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: event not found",
        ),
    },
    "test_get_event_response_body": {
        "id": "EVENT-009",
        "description": "Fetch event and verify response body fields",
        "api": "GET /api/events/{event_id}",
        "inputs": "valid event id, no auth",
        "expected": _out(
            "Status: 200 OK",
            "name: 'Robotics Hackathon'",
            "category: 'workshop'",
            "event_date: '2026-11-01'",
            "venue: 'auditorium'",
        ),
    },
    "test_get_event_winner_fields_null_when_no_winners": {
        "id": "EVENT-010",
        "description": "Winner fields are null when no winners exist",
        "api": "GET /api/events/{event_id}",
        "inputs": "event id with no winners",
        "expected": _out(
            "Status: 200 OK",
            "winner_name: null",
            "winner_project_url: null",
        ),
    },
    "test_get_event_does_not_expose_private_fields": {
        "id": "EVENT-011",
        "description": "Private fields are not exposed publicly",
        "api": "GET /api/events/{event_id}",
        "inputs": "valid event id, no auth",
        "expected": _out(
            "Status: 200 OK",
            "response excludes: registration_deadline, status, created_at, updated_at",
        ),
    },
    "test_get_password_hash_differs_from_plaintext": {
        "id": "SEC-001",
        "description": "Hashed password differs from plaintext",
        "api": "security.get_password_hash()",
        "inputs": "password='supersecret'",
        "expected": _out(
            "hashed != 'supersecret'",
            "hashed.startswith(('$2', '$2a', '$2b')) is True",
        ),
    },
    "test_verify_password_correct": {
        "id": "SEC-002",
        "description": "Verify a correct password",
        "api": "security.verify_password()",
        "inputs": "plain='supersecret'<br>hashed=hash('supersecret')",
        "expected": _out("Result: True"),
    },
    "test_verify_password_wrong": {
        "id": "SEC-003",
        "description": "Verify an incorrect password",
        "api": "security.verify_password()",
        "inputs": "plain='wrongpass'<br>hashed=hash('supersecret')",
        "expected": _out("Result: False"),
    },
    "test_create_access_token_returns_jwt": {
        "id": "SEC-004",
        "description": "Create access token returns a JWT",
        "api": "security.create_access_token()",
        "inputs": "subject='user-123'",
        "expected": _out(
            "token is str",
            "token.count('.') == 2",
        ),
    },
    "test_decode_access_token_returns_original_subject": {
        "id": "SEC-005",
        "description": "Decode token returns the original subject",
        "api": "security.decode_access_token()",
        "inputs": "token from create_access_token",
        "expected": _out("payload['sub'] == <original subject>"),
    },
    "test_demo_intentional_failure": {
        "id": "DEMO-001",
        "description": "Intentional failing test to verify failure rendering",
        "api": "demo (temporary)",
        "inputs": "1 + 1",
        "expected": _out(
            "Status: 200 OK",
            "Result: 3",
        ),
    },
}

TEST_FILE_DIRS = [
    BASE_DIR / "integration",
    BASE_DIR / "unit",
]


def _implemented_tests() -> set[str]:
    """Names of ``test_*`` functions that actually exist in the suite."""
    names: set[str] = set()
    for directory in TEST_FILE_DIRS:
        for file in sorted(directory.rglob("*.py")):
            for line in file.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped.startswith("def test_"):
                    names.add(stripped[len("def ") : stripped.index("(")])
    return names


def _load_results() -> dict[str, str]:
    """Map test node id -> outcome (passed/failed) from the results log."""
    if not RESULTS_LOG.exists():
        return {}
    data = json.loads(RESULTS_LOG.read_text(encoding="utf-8"))
    return {entry["test"]: entry["outcome"] for entry in data}


def generate() -> str:
    """Build the markdown matrix document."""
    implemented = _implemented_tests()
    results = _load_results()

    rows = [
        (func, meta)
        for func, meta in TESTS.items()
        if func in implemented
    ]

    lines = [
        "# API Test Matrix",
        "",
        "Registered `test_*` functions. Endpoints without tests are omitted.",
        "",
        "> Auto-generated by `tests/tools/generate_test_matrix.py`. Do not edit by hand.",
        "",
        "| Test ID | Description | API / Function | Inputs | Expected Output | Actual Output | Result |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for func, meta in rows:
        outcome = _latest_outcome(results, func)
        actual = meta["expected"] if outcome == "passed" else _actual_outcome(outcome)
        result = _result(outcome)
        lines.append(
            f"| {meta['id']} | {meta['description']} | `{meta['api']}` | "
            f"{meta['inputs']} | {meta['expected']} | {actual} | {result} |"
        )

    lines.append("")
    return "\n".join(lines)


def _latest_outcome(results: dict[str, str], func: str) -> str | None:
    """Outcome of the most recent run of ``func`` (or None if never run)."""
    for node, res in results.items():
        if node.rsplit("::", 1)[-1].startswith(func):
            return res
    return None


def _actual_outcome(outcome: str | None) -> str:
    """Build the 'Actual Output' cell for a non-passing test."""
    if outcome == "failed":
        return _out("Test failed - see pytest output")
    return _out("Not run yet")


def _result(outcome: str | None) -> str:
    """Result column value."""
    if outcome == "passed":
        return "Success"
    if outcome == "failed":
        return "Fail"
    return "Not Run"


def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(generate(), encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()