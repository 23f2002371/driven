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
ACTUAL_LOG = BASE_DIR / "reports" / "actual_outputs.json"


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
        "description": "Register with a password shorter than 6 chars",
        "api": "POST /api/auth/register",
        "inputs": "password='short'",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "Message: password must be at least 6 characters",
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
    "test_register_empty_full_name": {
        "id": "AUTH-012",
        "description": "Register with an empty full_name",
        "api": "POST /api/auth/register",
        "inputs": "full_name=''",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "full_name violates min_length=1",
        ),
    },
    "test_register_whitespace_only_full_name": {
        "id": "AUTH-013",
        "description": "Register with a whitespace-only full_name",
        "api": "POST /api/auth/register",
        "inputs": "full_name='   '",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "whitespace-only names must be rejected",
        ),
    },
    "test_register_full_name_not_trimmed": {
        "id": "AUTH-014",
        "description": "Register with a padded full_name is normalized",
        "api": "POST /api/auth/register",
        "inputs": "full_name='  Jane Doe  '",
        "expected": _out(
            "Status: 201 Created",
            "stored full_name trimmed: 'Jane Doe'",
        ),
    },
    "test_register_email_normalized_whitespace": {
        "id": "AUTH-015",
        "description": "Register email whitespace is stripped",
        "api": "POST /api/auth/register",
        "inputs": "email='  jane@example.com  '",
        "expected": _out(
            "Status: 201 Created",
            "stored email: 'jane@example.com'",
        ),
    },
    "test_register_duplicate_email_different_case": {
        "id": "AUTH-016",
        "description": "Register duplicate email with different casing",
        "api": "POST /api/auth/register",
        "inputs": "'Case@example.com' after 'case@example.com'",
        "expected": _out(
            "Status: 409 Conflict",
            "emails treated case-insensitively",
        ),
    },
    "test_register_password_boundary_lengths": {
        "id": "AUTH-017",
        "description": "Register password at exact min/max lengths",
        "api": "POST /api/auth/register",
        "inputs": "password length 6 and 72",
        "expected": _out(
            "Status: 201 Created",
            "boundary lengths accepted",
        ),
    },
    "test_register_password_over_max_length": {
        "id": "AUTH-018",
        "description": "Register with password over max length",
        "api": "POST /api/auth/register",
        "inputs": "password length 256",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "max_length=255 exceeded",
        ),
    },
    "test_register_whitespace_only_password": {
        "id": "AUTH-019",
        "description": "Register with a whitespace-only password",
        "api": "POST /api/auth/register",
        "inputs": "password='        '",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "weak / whitespace-only password rejected",
        ),
    },
    "test_register_full_name_over_max_length": {
        "id": "AUTH-020",
        "description": "Register with full_name over max length",
        "api": "POST /api/auth/register",
        "inputs": "full_name length 101",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "max_length=100 exceeded",
        ),
    },
    "test_register_email_over_max_length": {
        "id": "AUTH-021",
        "description": "Register with email over max length",
        "api": "POST /api/auth/register",
        "inputs": "email length > 150",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "max_length=150 exceeded",
        ),
    },
    "test_register_password_at_bcrypt_limit_roundtrips": {
        "id": "AUTH-022",
        "description": "Password at the bcrypt 72-byte limit round-trips",
        "api": "POST /api/auth/register + login",
        "inputs": "password = 'A'*72",
        "expected": _out(
            "Status: 201 Created on register",
            "Status: 200 OK on login",
            "max_length=72 prevents bcrypt truncation",
        ),
    },
    "test_register_role_smuggling_rejected": {
        "id": "AUTH-023",
        "description": "Role / identity smuggling via extra fields is rejected",
        "api": "POST /api/auth/register",
        "inputs": "extra fields: role, is_admin, id",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "extra='forbid' on UserCreate",
        ),
    },
    "test_register_malformed_json": {
        "id": "AUTH-024",
        "description": "Register with a malformed JSON body",
        "api": "POST /api/auth/register",
        "inputs": "body='{\"full_name\": \"Jane Doe\",'",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "JSON decode error",
        ),
    },
    "test_register_wrong_content_type": {
        "id": "AUTH-025",
        "description": "Register with a wrong Content-Type",
        "api": "POST /api/auth/register",
        "inputs": "form-encoded body",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "non-JSON body rejected",
        ),
    },
    "test_register_sql_injection_safe": {
        "id": "AUTH-026",
        "description": "SQL injection payload is stored literally",
        "api": "POST /api/auth/register",
        "inputs": "full_name=\"x'; DROP TABLE users; --\"",
        "expected": _out(
            "Status: 201 Created",
            "stored as literal text",
        ),
    },
    "test_register_xss_payload_stored_literal": {
        "id": "AUTH-027",
        "description": "XSS payload is stored literally",
        "api": "POST /api/auth/register",
        "inputs": "full_name='<script>alert(1)</script>'",
        "expected": _out(
            "Status: 201 Created",
            "stored as literal data (escaping is a rendering concern)",
        ),
    },
    "test_register_unicode_and_emoji_full_name": {
        "id": "AUTH-028",
        "description": "Unicode and emoji full_name accepted",
        "api": "POST /api/auth/register",
        "inputs": "full_name='Jöhn Müller 🚀 中文'",
        "expected": _out("Status: 201 Created"),
    },
    "test_register_null_field_values": {
        "id": "AUTH-029",
        "description": "Register with null required fields",
        "api": "POST /api/auth/register",
        "inputs": "full_name/email/password = null",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "null rejected for required string fields",
        ),
    },
    "test_register_invalid_http_method": {
        "id": "AUTH-030",
        "description": "Unsupported HTTP method on register",
        "api": "POST /api/auth/register",
        "inputs": "GET/PUT/PATCH/DELETE",
        "expected": _out("Status: 405 Method Not Allowed"),
    },
    "test_register_concurrent_duplicate": {
        "id": "AUTH-031",
        "description": "Concurrent duplicate registrations race safely",
        "api": "POST /api/auth/register",
        "inputs": "5 threads, same email",
        "expected": _out(
            "Exactly one 201 Created",
            "remaining 409 Conflict",
            "no 500",
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
    "test_login_empty_password": {
        "id": "AUTH-032",
        "description": "Login with an empty password",
        "api": "POST /api/auth/login",
        "inputs": "password=''",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "min_length=1 violated",
        ),
    },
    "test_login_whitespace_password": {
        "id": "AUTH-033",
        "description": "Login with a whitespace-only password",
        "api": "POST /api/auth/login",
        "inputs": "password='   '",
        "expected": _out(
            "Status: 401 Unauthorized",
            "whitespace password never authenticates",
        ),
    },
    "test_login_null_credentials": {
        "id": "AUTH-034",
        "description": "Login with null credentials",
        "api": "POST /api/auth/login",
        "inputs": "email=null, password=null",
        "expected": _out("Status: 422 Unprocessable Entity"),
    },
    "test_login_email_whitespace_normalized": {
        "id": "AUTH-035",
        "description": "Login email whitespace is normalized",
        "api": "POST /api/auth/login",
        "inputs": "email='  user@example.com  '",
        "expected": _out(
            "Status: 200 OK",
            "whitespace stripped before lookup",
        ),
    },
    "test_login_email_case_insensitive": {
        "id": "AUTH-036",
        "description": "Login email case-sensitivity (known gap)",
        "api": "POST /api/auth/login",
        "inputs": "login as 'CASE@EXAMPLE.COM'",
        "expected": _out(
            "Status: 401 Unauthorized",
            "known gap: no login email normalization yet",
        ),
    },
    "test_login_malformed_json": {
        "id": "AUTH-037",
        "description": "Login with a malformed JSON body",
        "api": "POST /api/auth/login",
        "inputs": "body='{\"email\": \"x@y.com\"'",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "JSON decode error",
        ),
    },
    "test_login_wrong_content_type": {
        "id": "AUTH-038",
        "description": "Login with a wrong Content-Type",
        "api": "POST /api/auth/login",
        "inputs": "form-encoded body",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "non-JSON body rejected",
        ),
    },
    "test_login_sql_injection": {
        "id": "AUTH-039",
        "description": "SQL injection in credentials is neutralized",
        "api": "POST /api/auth/login",
        "inputs": "password=\"anything' OR '1'='1' --\"",
        "expected": _out(
            "Status: 401 Unauthorized",
            "injection treated as plain text",
        ),
    },
    "test_login_xss_in_password": {
        "id": "AUTH-040",
        "description": "XSS payload in password does not authenticate",
        "api": "POST /api/auth/login",
        "inputs": "password='<script>alert(1)</script>'",
        "expected": _out("Status: 401 Unauthorized"),
    },
    "test_login_very_long_password": {
        "id": "AUTH-041",
        "description": "Oversized password is rejected without crashing",
        "api": "POST /api/auth/login",
        "inputs": "password length 10_000",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "max_length=72 rejects it (no PasswordSizeError crash)",
        ),
    },
    "test_login_extra_field_rejected": {
        "id": "AUTH-042",
        "description": "Unexpected extra field on login is rejected",
        "api": "POST /api/auth/login",
        "inputs": "body includes extra='sneaky'",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "extra fields forbidden like register",
        ),
    },
    "test_login_unicode_password_roundtrip": {
        "id": "AUTH-043",
        "description": "Unicode password round-trips exactly",
        "api": "POST /api/auth/login",
        "inputs": "password='pässwörd-🔑'",
        "expected": _out("Status: 200 OK"),
    },
    "test_login_invalid_http_method": {
        "id": "AUTH-044",
        "description": "Unsupported HTTP method on login",
        "api": "POST /api/auth/login",
        "inputs": "GET/PUT/PATCH/DELETE",
        "expected": _out("Status: 405 Method Not Allowed"),
    },
    "test_me_missing_auth_header": {
        "id": "AUTH-045",
        "description": "GET /me without an Authorization header",
        "api": "GET /api/auth/me",
        "inputs": "no header",
        "expected": _out("Status: 401 Unauthorized"),
    },
    "test_me_malformed_auth_header": {
        "id": "AUTH-046",
        "description": "GET /me with a malformed Authorization header",
        "api": "GET /api/auth/me",
        "inputs": "Authorization: 'Token <uuid>'",
        "expected": _out(
            "Status: 401 Unauthorized",
            "must be Bearer <token>",
        ),
    },
    "test_me_random_garbage_token": {
        "id": "AUTH-047",
        "description": "GET /me with a random garbage token",
        "api": "GET /api/auth/me",
        "inputs": "Authorization: 'Bearer abc.def.ghi'",
        "expected": _out("Status: 401 Unauthorized"),
    },
    "test_me_expired_token": {
        "id": "AUTH-048",
        "description": "GET /me with an expired JWT",
        "api": "GET /api/auth/me",
        "inputs": "token with exp in the past",
        "expected": _out("Status: 401 Unauthorized"),
    },
    "test_me_tampered_token": {
        "id": "AUTH-049",
        "description": "GET /me with a tampered token payload",
        "api": "GET /api/auth/me",
        "inputs": "valid token with forged sub",
        "expected": _out("Status: 401 Unauthorized"),
    },
    "test_me_token_signed_with_wrong_secret": {
        "id": "AUTH-050",
        "description": "GET /me with a token signed by an unknown key",
        "api": "GET /api/auth/me",
        "inputs": "token signed with attacker secret",
        "expected": _out("Status: 401 Unauthorized"),
    },
    "test_me_token_for_deleted_user": {
        "id": "AUTH-051",
        "description": "GET /me with a token for a deleted user",
        "api": "GET /api/auth/me",
        "inputs": "valid token, subject removed from DB",
        "expected": _out("Status: 401 Unauthorized"),
    },
    "test_create_event_as_club_admin": {
        "id": "EVENT-001",
        "description": "Club admin creates an event without cover image",
        "api": "POST /api/events",
        "inputs": "valid EventCreate form data (no cover image)",
        "expected": _out(
            "Status: 201 Created",
            "name: 'Intro to AI Workshop'",
            "status: 'pending'",
            "cover_image_url: null",
        ),
    },
    "test_create_event_with_valid_jpeg_image_success": {
        "id": "EVENT-IMG-001",
        "description": "Create event with valid JPEG cover image",
        "api": "POST /api/events",
        "inputs": "multipart/form-data with valid JPEG file",
        "expected": _out(
            "Status: 201 Created",
            "Cloudinary upload called",
            "cover_image_url: secure_url saved",
        ),
    },
    "test_create_event_with_valid_png_image_success": {
        "id": "EVENT-IMG-002",
        "description": "Create event with valid PNG cover image",
        "api": "POST /api/events",
        "inputs": "multipart/form-data with valid PNG file",
        "expected": _out(
            "Status: 201 Created",
            "cover_image_url: secure_url saved",
        ),
    },
    "test_create_event_with_valid_webp_image_success": {
        "id": "EVENT-IMG-003",
        "description": "Create event with valid WebP cover image",
        "api": "POST /api/events",
        "inputs": "multipart/form-data with valid WebP file",
        "expected": _out(
            "Status: 201 Created",
            "cover_image_url: secure_url saved",
        ),
    },
    "test_create_event_invalid_image_type_rejected": {
        "id": "EVENT-IMG-004",
        "description": "Reject unsupported cover image MIME type",
        "api": "POST /api/events",
        "inputs": "multipart/form-data with image/gif file",
        "expected": _out(
            "Status: 400 Bad Request",
            "detail: Unsupported image type",
            "Event not created in DB",
        ),
    },
    "test_create_event_image_exceeds_5mb_rejected": {
        "id": "EVENT-IMG-005",
        "description": "Reject cover image exceeding 5MB limit",
        "api": "POST /api/events",
        "inputs": "multipart/form-data with >5MB file",
        "expected": _out(
            "Status: 400 Bad Request",
            "detail: Image size exceeds maximum limit",
            "Event not created in DB",
        ),
    },
    "test_create_event_cloudinary_failure_rollback": {
        "id": "EVENT-IMG-006",
        "description": "Cloudinary failure returns 500 and prevents DB save",
        "api": "POST /api/events",
        "inputs": "multipart/form-data, Cloudinary upload failure",
        "expected": _out(
            "Status: 500 Internal Server Error",
            "Event not created/persisted in DB",
        ),
    },
    "test_create_event_stored_url_is_not_base64_or_local": {
        "id": "EVENT-IMG-007",
        "description": "Stored cover_image_url is strictly Cloudinary secure_url",
        "api": "POST /api/events",
        "inputs": "multipart/form-data with cover image",
        "expected": _out(
            "Status: 201 Created",
            "cover_image_url is https://res.cloudinary.com/...",
            "Not Base64, blob:, or local path",
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
    "test_create_registration_uses_submitted_student_profile": {
        "id": "EVENT-012",
        "description": "Register a student with a submitted profile",
        "api": "POST /api/events/registrations",
        "inputs": "valid registration payload, student token",
        "expected": _out(
            "Status: 201 Created",
            "event_id: <event id>",
            "student_id: <student id>",
            "registration_status: 'pending'",
            "attendance_status: 'absent'",
        ),
    },
    "test_create_registration_syncs_profile_to_student": {
        "id": "EVENT-013",
        "description": "Registration syncs submitted profile to the Student row",
        "api": "POST /api/events/registrations",
        "inputs": "valid registration payload, student token",
        "expected": _out(
            "Status: 201 Created",
            "student_id: 'CS0002'",
            "phone: '12345'",
            "github: 'gh'",
        ),
    },
    "test_create_registration_creates_student_for_user": {
        "id": "EVENT-014",
        "description": "First registration creates a Student for the user",
        "api": "POST /api/events/registrations",
        "inputs": "valid registration payload, student token",
        "expected": _out("Status: 201 Created", "student row created"),
    },
    "test_create_registration_duplicate_conflict": {
        "id": "EVENT-015",
        "description": "Duplicate registration for the same event",
        "api": "POST /api/events/registrations",
        "inputs": "same payload submitted twice",
        "expected": _out(
            "First: 201 Created",
            "Second: 409 Conflict",
            "Message: Already registered for this event",
        ),
    },
    "test_create_registration_rejects_unexpected_field": {
        "id": "EVENT-025",
        "description": "Register with an unexpected field is rejected",
        "api": "POST /api/events/registrations",
        "inputs": "valid payload plus an unexpected field",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "unexpected field rejected",
        ),
    },
    "test_update_registration_updates_editable_fields": {
        "id": "EVENT-016",
        "description": "Student updates their own registration",
        "api": "PATCH /api/events/registrations/{id}",
        "inputs": "team_name, github, domains",
        "expected": _out(
            "Status: 200 OK",
            "team_name: 'Team B'",
            "student.github: 'gh2'",
        ),
    },
    "test_update_registration_rejects_protected_fields": {
        "id": "EVENT-028",
        "description": "Updating protected fields is rejected",
        "api": "PATCH /api/events/registrations/{id}",
        "inputs": "payload with registration_status",
        "expected": _out("Status: 422 Unprocessable Entity"),
    },
    "test_update_other_students_registration_forbidden": {
        "id": "EVENT-017",
        "description": "Trying to update another student's registration",
        "api": "PATCH /api/events/registrations/{id}",
        "inputs": "other student's registration id",
        "expected": _out("Status: 403 Forbidden"),
    },
    "test_get_registration_returns_embedded_student_profile": {
        "id": "EVENT-018",
        "description": "Fetch the student's own registration",
        "api": "GET /api/events/registrations/{id}",
        "inputs": "valid registration id, student token",
        "expected": _out(
            "Status: 200 OK",
            "registration_status: 'pending'",
            "student.student_id: 'CS0012'",
        ),
    },
    "test_upsert_winners_creates_all_positions": {
        "id": "EVENT-019",
        "description": "Upsert all three winner positions",
        "api": "PUT /api/events/winners",
        "inputs": "payload with first/second/third positions",
        "expected": _out(
            "Status: 200 OK",
            "3 winners",
            "positions: first, second, third",
            "first.project_name: 'Alpha'",
        ),
    },
    "test_upsert_winners_updates_only_supplied_positions": {
        "id": "EVENT-020",
        "description": "Upsert only updates supplied positions",
        "api": "PUT /api/events/winners",
        "inputs": "partial payload with just 'first'",
        "expected": _out(
            "Status: 200 OK",
            "first: 'Alpha-Updated'",
            "second: 'Beta'",
        ),
    },
    "test_get_event_winners_returns_all_positions": {
        "id": "EVENT-021",
        "description": "Fetch winners for an event",
        "api": "GET /api/events/{event_id}/winners",
        "inputs": "event id with winners",
        "expected": _out(
            "Status: 200 OK",
            "3 winners",
            "positions: first, second, third",
        ),
    },
    "test_declare_winner_for_registration_of_event": {
        "id": "EVENT-026",
        "description": "Declare a winner for a registration of the same event",
        "api": "POST /api/events/winners",
        "inputs": "registration that belongs to the event, first position",
        "expected": _out(
            "Status: 201 Created",
            "event_id: <event id>",
            "registration_id: <registration id>",
            "project_name: 'Alpha'",
        ),
    },
    "test_generate_certificates_for_event": {
        "id": "EVENT-022",
        "description": "Generate certificates for all registrations",
        "api": "POST /api/events/{event_id}/certificates",
        "inputs": "event with 3 registrations, one second-place winner",
        "expected": _out(
            "Status: 201 Created",
            "3 certificates",
            "second-place: 'second'",
            "others: 'participation'",
        ),
    },
    "test_generate_certificates_skips_existing": {
        "id": "EVENT-023",
        "description": "Re-running generates no duplicates",
        "api": "POST /api/events/{event_id}/certificates",
        "inputs": "generate twice",
        "expected": _out(
            "First: 201 Created, 2 certificates",
            "Second: 201 Created, empty list",
        ),
    },
    "test_get_student_certificates": {
        "id": "EVENT-024",
        "description": "Fetch a student's certificates",
        "api": "GET /api/students/{student_id}/certificates",
        "inputs": "student with one certificate",
        "expected": _out(
            "Status: 200 OK",
            "1 certificate",
            "certificate_type: 'participation'",
            "event_name: 'Cert Event'",
        ),
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
    "test_create_equipment_success": {
        "id": "INV-001",
        "description": "Create a piece of equipment",
        "api": "POST /api/equipment",
        "inputs": "valid equipment payload (club admin)",
        "expected": _out(
            "Status: 201 Created",
            "name: 'Oscilloscope'",
            "total_quantity: 10",
            "available_quantity: 10",
        ),
    },
    "test_create_equipment_duplicate_request": {
        "id": "INV-024",
        "description": "Duplicate create request for the same equipment",
        "api": "POST /api/equipment",
        "inputs": "identical create payload submitted twice",
        "expected": _out(
            "First: 201 Created",
            "Second: 409 Conflict",
        ),
    },
    "test_create_equipment_invalid_available_exceeds_total": {
        "id": "INV-002",
        "description": "available_quantity exceeds total_quantity",
        "api": "POST /api/equipment",
        "inputs": "total_quantity=5, available_quantity=6",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "Message: available_quantity cannot exceed total_quantity",
        ),
    },
    "test_create_equipment_total_quantity_validation": {
        "id": "INV-003",
        "description": "total_quantity must be at least 1",
        "api": "POST /api/equipment",
        "inputs": "total_quantity=0",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_create_equipment_empty_name": {
        "id": "INV-004",
        "description": "Equipment name cannot be empty",
        "api": "POST /api/equipment",
        "inputs": "name=''",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_create_equipment_rejects_extra_field": {
        "id": "INV-005",
        "description": "Unexpected field rejected via extra=forbid",
        "api": "POST /api/equipment",
        "inputs": "valid payload plus an unknown field",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_create_equipment_student_forbidden": {
        "id": "INV-006",
        "description": "Student cannot create equipment",
        "api": "POST /api/equipment",
        "inputs": "student token",
        "expected": _out(
            "Status: 403 Forbidden",
            "Message: Insufficient permissions",
        ),
    },
    "test_create_equipment_unauthenticated": {
        "id": "INV-007",
        "description": "Create equipment without a token",
        "api": "POST /api/equipment",
        "inputs": "no Authorization header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_increase_equipment_stock_success": {
        "id": "INV-008",
        "description": "Increase equipment stock",
        "api": "POST /api/equipment/stock/increase",
        "inputs": "equipment_id, increment_quantity=5",
        "expected": _out(
            "Status: 200 OK",
            "total_quantity: 15",
            "available_quantity: 15",
        ),
    },
    "test_increase_equipment_stock_not_found": {
        "id": "INV-009",
        "description": "Increase stock of a missing equipment",
        "api": "POST /api/equipment/stock/increase",
        "inputs": "random equipment_id",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Equipment not found",
        ),
    },
    "test_increase_equipment_stock_zero_increment": {
        "id": "INV-010",
        "description": "increment_quantity must be at least 1",
        "api": "POST /api/equipment/stock/increase",
        "inputs": "increment_quantity=0",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_increase_equipment_stock_student_forbidden": {
        "id": "INV-011",
        "description": "Student cannot increase stock",
        "api": "POST /api/equipment/stock/increase",
        "inputs": "student token",
        "expected": _out(
            "Status: 403 Forbidden",
            "Message: Insufficient permissions",
        ),
    },
    "test_increase_equipment_stock_unauthenticated": {
        "id": "INV-012",
        "description": "Increase stock without a token",
        "api": "POST /api/equipment/stock/increase",
        "inputs": "no Authorization header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_borrow_equipment_new_borrow_created": {
        "id": "INV-013",
        "description": "Student borrows equipment for the first time",
        "api": "POST /api/equipment/borrow",
        "inputs": "equipment_id, borrowed_quantity=2, return_date",
        "expected": _out(
            "Status: 201 Created",
            "borrowed_quantity: 2",
            "student_email: 'student@example.com'",
        ),
    },
    "test_borrow_equipment_existing_borrow_updated": {
        "id": "INV-014",
        "description": "Borrowing again increases borrowed_quantity",
        "api": "POST /api/equipment/borrow",
        "inputs": "borrow 2 then borrow 3 for the same equipment",
        "expected": _out(
            "First: 201 Created",
            "Second: 200 OK",
            "borrowed_quantity: 5",
        ),
    },
    "test_borrow_equipment_exceeds_available_stock": {
        "id": "INV-015",
        "description": "Requested quantity exceeds available stock",
        "api": "POST /api/equipment/borrow",
        "inputs": "available_quantity=1, borrowed_quantity=5",
        "expected": _out(
            "Status: 400 Bad Request",
            "Message: Requested quantity exceeds available stock.",
        ),
    },
    "test_borrow_equipment_not_found": {
        "id": "INV-016",
        "description": "Borrow a missing equipment",
        "api": "POST /api/equipment/borrow",
        "inputs": "random equipment_id",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Equipment not found",
        ),
    },
    "test_borrow_equipment_zero_quantity": {
        "id": "INV-017",
        "description": "borrowed_quantity must be at least 1",
        "api": "POST /api/equipment/borrow",
        "inputs": "borrowed_quantity=0",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_borrow_equipment_admin_forbidden": {
        "id": "INV-018",
        "description": "Club admin cannot borrow equipment",
        "api": "POST /api/equipment/borrow",
        "inputs": "club admin token",
        "expected": _out(
            "Status: 403 Forbidden",
            "Message: Insufficient permissions",
        ),
    },
    "test_borrow_equipment_unauthenticated": {
        "id": "INV-019",
        "description": "Borrow equipment without a token",
        "api": "POST /api/equipment/borrow",
        "inputs": "no Authorization header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_delete_borrow_detail_restores_stock": {
        "id": "INV-020",
        "description": "Delete a borrow detail restores equipment stock",
        "api": "DELETE /api/borrow-details/{borrow_detail_id}",
        "inputs": "borrow_detail_id matching an existing borrow",
        "expected": _out(
            "Status: 204 No Content",
            "available_quantity restored to 10",
        ),
    },
    "test_delete_borrow_detail_not_found": {
        "id": "INV-021",
        "description": "Delete a missing borrow detail",
        "api": "DELETE /api/borrow-details/{borrow_detail_id}",
        "inputs": "random borrow_detail_id",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Borrow detail not found",
        ),
    },
    "test_delete_borrow_detail_student_forbidden": {
        "id": "INV-022",
        "description": "Student cannot delete a borrow detail",
        "api": "DELETE /api/borrow-details/{borrow_detail_id}",
        "inputs": "student token",
        "expected": _out(
            "Status: 403 Forbidden",
            "Message: Insufficient permissions",
        ),
    },
    "test_delete_borrow_detail_unauthenticated": {
        "id": "INV-023",
        "description": "Delete borrow detail without a token",
        "api": "DELETE /api/borrow-details/{borrow_detail_id}",
        "inputs": "no Authorization header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_create_discussion_thread_success": {
        "id": "SD-001",
        "description": "Create the discussion thread for an event",
        "api": "POST /api/events/{event_id}/discussion",
        "inputs": "event_id, title='Intro Thread' (club admin)",
        "expected": _out(
            "Status: 201 Created",
            "event_id: <event id>",
            "title: 'Intro Thread'",
            "creator_name: 'Forum User'",
        ),
    },
    "test_create_discussion_thread_duplicate_conflict": {
        "id": "SD-002",
        "description": "Only one discussion thread is allowed per event",
        "api": "POST /api/events/{event_id}/discussion",
        "inputs": "create twice for the same event",
        "expected": _out(
            "First: 201 Created",
            "Second: 409 Conflict",
        ),
    },
    "test_create_discussion_thread_event_not_found": {
        "id": "SD-003",
        "description": "Create a thread for a missing event",
        "api": "POST /api/events/{event_id}/discussion",
        "inputs": "random event_id",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Event not found",
        ),
    },
    "test_create_discussion_thread_student_forbidden": {
        "id": "SD-004",
        "description": "Student cannot create a thread",
        "api": "POST /api/events/{event_id}/discussion",
        "inputs": "student token",
        "expected": _out(
            "Status: 403 Forbidden",
            "Message: Insufficient permissions",
        ),
    },
    "test_create_discussion_thread_unauthenticated": {
        "id": "SD-005",
        "description": "Create a thread without a token",
        "api": "POST /api/events/{event_id}/discussion",
        "inputs": "no Authorization header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_get_discussion_thread_success": {
        "id": "SD-006",
        "description": "Fetch an event's discussion thread",
        "api": "GET /api/events/{event_id}/discussion",
        "inputs": "event with an existing thread",
        "expected": _out(
            "Status: 200 OK",
            "title: 'My Thread'",
        ),
    },
    "test_get_discussion_thread_requires_auth": {
        "id": "SD-007",
        "description": "Fetching an event's thread requires authentication",
        "api": "GET /api/events/{event_id}/discussion",
        "inputs": "no Authorization header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_get_discussion_thread_not_found": {
        "id": "SD-008",
        "description": "Fetch a thread for an event without one",
        "api": "GET /api/events/{event_id}/discussion",
        "inputs": "event with no thread",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Discussion thread not found",
        ),
    },
    "test_create_message_top_level_success": {
        "id": "SD-009",
        "description": "Post a top-level message",
        "api": "POST /api/discussion/{thread_id}/messages",
        "inputs": "thread_id, message (authenticated)",
        "expected": _out(
            "Status: 201 Created",
            "message: 'Can anyone join?'",
            "author_name: 'Forum User'",
            "replies: []",
        ),
    },
    "test_create_message_student_reply": {
        "id": "SD-010",
        "description": "Student replies to a message",
        "api": "POST /api/discussion/{thread_id}/messages",
        "inputs": "thread_id, parent_message_id, message",
        "expected": _out(
            "Status: 201 Created",
            "message: 'Can first years participate?'",
        ),
    },
    "test_create_message_thread_not_found": {
        "id": "SD-011",
        "description": "Post to a missing thread",
        "api": "POST /api/discussion/{thread_id}/messages",
        "inputs": "random thread_id",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Discussion thread not found",
        ),
    },
    "test_create_message_parent_not_found": {
        "id": "SD-012",
        "description": "Reply to a missing parent message",
        "api": "POST /api/discussion/{thread_id}/messages",
        "inputs": "random parent_message_id",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Parent message not found",
        ),
    },
    "test_create_message_unauthenticated": {
        "id": "SD-013",
        "description": "Post a message without a token",
        "api": "POST /api/discussion/{thread_id}/messages",
        "inputs": "no Authorization header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_update_message_owner_success": {
        "id": "SD-014",
        "description": "Message owner edits their own message",
        "api": "PATCH /api/messages/{message_id}",
        "inputs": "message_id, new message (owner token)",
        "expected": _out(
            "Status: 200 OK",
            "message: 'Edited by owner'",
        ),
    },
    "test_update_message_other_student_forbidden": {
        "id": "SD-015",
        "description": "Another student cannot edit a message",
        "api": "PATCH /api/messages/{message_id}",
        "inputs": "message_id, new message (other student token)",
        "expected": _out(
            "Status: 403 Forbidden",
            "Message: Not allowed to edit this message",
        ),
    },
    "test_update_message_club_admin_forbidden": {
        "id": "SD-016",
        "description": "Club admin cannot edit another user's message",
        "api": "PATCH /api/messages/{message_id}",
        "inputs": "message_id, new message (club admin token)",
        "expected": _out(
            "Status: 403 Forbidden",
            "Message: Not allowed to edit this message",
        ),
    },
    "test_update_message_not_found": {
        "id": "SD-017",
        "description": "Edit a missing message",
        "api": "PATCH /api/messages/{message_id}",
        "inputs": "random message_id",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Message not found",
        ),
    },
    "test_delete_message_owner_success": {
        "id": "SD-018",
        "description": "Owner soft-deletes their own message",
        "api": "DELETE /api/messages/{message_id}",
        "inputs": "message_id (owner token)",
        "expected": _out(
            "Status: 204 No Content",
            "is_deleted: True",
            "message: '[deleted]'",
        ),
    },
    "test_delete_message_other_student_forbidden": {
        "id": "SD-019",
        "description": "Another student cannot delete a message",
        "api": "DELETE /api/messages/{message_id}",
        "inputs": "message_id (other student token)",
        "expected": _out(
            "Status: 403 Forbidden",
            "Message: Not allowed to delete this message",
        ),
    },
    "test_delete_message_unauthenticated": {
        "id": "SD-020",
        "description": "Delete a message without a token",
        "api": "DELETE /api/messages/{message_id}",
        "inputs": "no Authorization header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_get_messages_nested_tree": {
        "id": "SD-021",
        "description": "Fetch the whole discussion as a nested tree",
        "api": "GET /api/discussion/{thread_id}/messages",
        "inputs": "thread with a root, reply and nested reply",
        "expected": _out(
            "Status: 200 OK",
            "2 top-level messages",
            "root has 1 reply",
            "reply has 1 nested reply: 'Yes.'",
        ),
    },
    "test_get_messages_deleted_message_keeps_replies": {
        "id": "SD-022",
        "description": "Deleted message shows [deleted] and keeps its replies",
        "api": "GET /api/discussion/{thread_id}/messages",
        "inputs": "thread with a deleted root message and a reply",
        "expected": _out(
            "Status: 200 OK",
            "root message: '[deleted]'",
            "1 reply: 'Admin answer'",
        ),
    },
    "test_get_messages_thread_not_found": {
        "id": "SD-023",
        "description": "Fetch messages of a missing thread",
        "api": "GET /api/discussion/{thread_id}/messages",
        "inputs": "random thread_id",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Discussion thread not found",
        ),
    },
    "test_create_bounty_success": {
        "id": "BN-001",
        "description": "Club admin creates a bounty",
        "api": "POST /api/bounties",
        "inputs": "valid BountyCreate payload with technology + responsibilities",
        "expected": _out(
            "Status: 201 Created",
            "title: 'Build Club Website'",
            "status: 'open'",
            "created_by: <admin id>",
            "domain: WEB_DEVELOPMENT",
        ),
    },
    "test_create_bounty_as_student_forbidden": {
        "id": "BN-002",
        "description": "Student tries to create a bounty",
        "api": "POST /api/bounties",
        "inputs": "valid BountyCreate payload",
        "expected": _out(
            "Status: 403 Forbidden",
        ),
    },
    "test_create_bounty_unauthenticated": {
        "id": "BN-003",
        "description": "Create a bounty without a token",
        "api": "POST /api/bounties",
        "inputs": "valid BountyCreate payload, no auth header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_create_bounty_domain_not_found": {
        "id": "BN-004",
        "description": "Create a bounty with a missing domain",
        "api": "POST /api/bounties",
        "inputs": "domain_id=00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Domain not found",
        ),
    },
    "test_create_bounty_technology_not_found": {
        "id": "BN-005",
        "description": "Create a bounty with a missing technology",
        "api": "POST /api/bounties",
        "inputs": "technologies=[00000000-0000-0000-0000-000000000000]",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Technology not found",
        ),
    },
    "test_create_bounty_technology_wrong_domain": {
        "id": "BN-006",
        "description": "Technology that belongs to another domain is rejected",
        "api": "POST /api/bounties",
        "inputs": "web domain + pytorch (AI_ML) technology",
        "expected": _out(
            "Status: 400 Bad Request",
            "Message: Technology does not belong to the selected domain",
        ),
    },
    "test_create_bounty_status_field_rejected": {
        "id": "BN-007",
        "description": "Client-provided status/created_by/id are rejected",
        "api": "POST /api/bounties",
        "inputs": "payload plus status, created_by",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
            "extra='forbid' on BountyCreate",
        ),
    },
    "test_create_bounty_missing_required_field": {
        "id": "BN-008",
        "description": "Create a bounty without description",
        "api": "POST /api/bounties",
        "inputs": "valid payload minus description",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_create_bounty_negative_reward": {
        "id": "BN-009",
        "description": "Negative reward is rejected",
        "api": "POST /api/bounties",
        "inputs": "reward='-100'",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_update_bounty_fields_success": {
        "id": "BN-010",
        "description": "Admin updates bounty title and seats",
        "api": "PATCH /api/bounties/{bounty_id}",
        "inputs": "title + student_seats (status left out)",
        "expected": _out(
            "Status: 200 OK",
            "title: 'Updated Title'",
            "student_seats: 8",
            "status: 'open' (unchanged)",
        ),
    },
    "test_update_bounty_as_student_forbidden": {
        "id": "BN-011",
        "description": "Student tries to update a bounty",
        "api": "PATCH /api/bounties/{bounty_id}",
        "inputs": "student token",
        "expected": _out(
            "Status: 403 Forbidden",
        ),
    },
    "test_update_bounty_not_found": {
        "id": "BN-012",
        "description": "Update a non-existent bounty",
        "api": "PATCH /api/bounties/{bounty_id}",
        "inputs": "00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Bounty not found",
        ),
    },
    "test_update_bounty_status_field_rejected": {
        "id": "BN-013",
        "description": "Client-provided status/created_by/id are rejected",
        "api": "PATCH /api/bounties/{bounty_id}",
        "inputs": "payload plus status, created_by, id",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_update_bounty_replaces_technologies": {
        "id": "BN-014",
        "description": "Technologies are replaced, not merged",
        "api": "PATCH /api/bounties/{bounty_id}",
        "inputs": "technologies=[TYPESCRIPT] after bounties has REACT",
        "expected": _out(
            "Status: 200 OK",
            "technologies: ['TYPESCRIPT']",
        ),
    },
    "test_update_bounty_replaces_responsibilities": {
        "id": "BN-015",
        "description": "Responsibilities are replaced wholesale",
        "api": "PATCH /api/bounties/{bounty_id}",
        "inputs": "responsibilities=[Design, Develop, Deploy]",
        "expected": _out(
            "Status: 200 OK",
            "responsibilities: Design, Develop, Deploy",
        ),
    },
    "test_update_bounty_technology_wrong_domain": {
        "id": "BN-016",
        "description": "Technology from another domain rejected on update",
        "api": "PATCH /api/bounties/{bounty_id}",
        "inputs": "technologies=[PYTORCH] on a WEB_DEVELOPMENT bounty",
        "expected": _out(
            "Status: 400 Bad Request",
        ),
    },
    "test_update_bounty_domain_changed_success": {
        "id": "BN-017",
        "description": "Admin switches the bounty domain together with its technology",
        "api": "PATCH /api/bounties/{bounty_id}",
        "inputs": "new domain_id=AI_ML, technologies=[NEXT_JS]",
        "expected": _out(
            "Status: 200 OK",
            "domain: AI_ML",
            "technologies: ['NEXT_JS']",
        ),
    },
    "test_update_bounty_domain_changed_wrong_technology": {
        "id": "BN-018",
        "description": "Orphaned technology rejected when the domain changes",
        "api": "PATCH /api/bounties/{bounty_id}",
        "inputs": "domain_id=AI_ML but technologies=[REACT (web)]",
        "expected": _out(
            "Status: 400 Bad Request",
        ),
    },
    "test_get_bounty_success": {
        "id": "BN-019",
        "description": "Student fetches an existing bounty with nested data",
        "api": "GET /api/bounties/{bounty_id}",
        "inputs": "bounty with 1 technology and 1 responsibility",
        "expected": _out(
            "Status: 200 OK",
            "status: 'open'",
            "domain: WEB_DEVELOPMENT",
            "technologies: ['REACT']",
        ),
    },
    "test_get_bounty_as_admin_or_lab_admin": {
        "id": "BN-020",
        "description": "Lab admin is permitted to read a bounty",
        "api": "GET /api/bounties/{bounty_id}",
        "inputs": "lab admin token",
        "expected": _out(
            "Status: 200 OK",
        ),
    },
    "test_get_bounty_not_found": {
        "id": "BN-021",
        "description": "Fetch a non-existent bounty",
        "api": "GET /api/bounties/{bounty_id}",
        "inputs": "00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Bounty not found",
        ),
    },
    "test_get_bounty_unauthenticated": {
        "id": "BN-022",
        "description": "Fetch a bounty without a token",
        "api": "GET /api/bounties/{bounty_id}",
        "inputs": "no auth header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_delete_bounty_success": {
        "id": "BN-023",
        "description": "Admin deletes a bounty",
        "api": "DELETE /api/bounties/{bounty_id}",
        "inputs": "existing bounty id",
        "expected": _out(
            "Status: 204 No Content",
            "bounty row removed",
        ),
    },
    "test_delete_bounty_as_student_forbidden": {
        "id": "BN-024",
        "description": "Student tries to delete a bounty",
        "api": "DELETE /api/bounties/{bounty_id}",
        "inputs": "student token",
        "expected": _out(
            "Status: 403 Forbidden",
        ),
    },
    "test_delete_bounty_not_found": {
        "id": "BN-025",
        "description": "Delete a non-existent bounty",
        "api": "DELETE /api/bounties/{bounty_id}",
        "inputs": "00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Bounty not found",
        ),
    },
    "test_create_application_success": {
        "id": "APP-001",
        "description": "Student applies to a bounty",
        "api": "POST /api/bounties/{bounty_id}/applications",
        "inputs": "availability + resume",
        "expected": _out(
            "Status: 201 Created",
            "status: 'pending'",
            "student_id: <student id>",
            "bounty.title: 'Direct Bounty'",
        ),
    },
    "test_create_application_status_field_rejected": {
        "id": "APP-002",
        "description": "Client-provided status/student_id rejected",
        "api": "POST /api/bounties/{bounty_id}/applications",
        "inputs": "payload plus status, student_id",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_create_application_as_admin_forbidden": {
        "id": "APP-003",
        "description": "Club admin cannot apply to a bounty",
        "api": "POST /api/bounties/{bounty_id}/applications",
        "inputs": "admin token",
        "expected": _out(
            "Status: 403 Forbidden",
        ),
    },
    "test_create_application_unauthenticated": {
        "id": "APP-004",
        "description": "Apply without a token",
        "api": "POST /api/bounties/{bounty_id}/applications",
        "inputs": "no auth header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_create_application_bounty_not_found": {
        "id": "APP-005",
        "description": "Apply to a non-existent bounty",
        "api": "POST /api/bounties/{bounty_id}/applications",
        "inputs": "00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Bounty not found",
        ),
    },
    "test_create_application_closed_bounty": {
        "id": "APP-006",
        "description": "Apply to a CLOSED bounty is rejected",
        "api": "POST /api/bounties/{bounty_id}/applications",
        "inputs": "bounty status=closed",
        "expected": _out(
            "Status: 409 Conflict",
            "Message: Bounty is not accepting applications",
        ),
    },
    "test_create_application_duplicate": {
        "id": "APP-007",
        "description": "Applying twice is a conflict",
        "api": "POST /api/bounties/{bounty_id}/applications",
        "inputs": "same student applies twice",
        "expected": _out(
            "First: 201 Created",
            "Second: 409 Conflict",
            "Message: You have already applied to this bounty",
        ),
    },
    "test_create_application_no_student_profile": {
        "id": "APP-008",
        "description": "Student without a profile cannot apply",
        "api": "POST /api/bounties/{bounty_id}/applications",
        "inputs": "student user with no Student row",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Student profile not found",
        ),
    },
    "test_create_application_missing_availability": {
        "id": "APP-009",
        "description": "Apply without availability",
        "api": "POST /api/bounties/{bounty_id}/applications",
        "inputs": "resume only",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_get_application_as_owner": {
        "id": "APP-010",
        "description": "Student fetches their own application",
        "api": "GET /api/applications/{application_id}",
        "inputs": "student token",
        "expected": _out(
            "Status: 200 OK",
            "status: 'accepted'",
            "bounty.title: 'Direct Bounty'",
        ),
    },
    "test_get_application_as_admin": {
        "id": "APP-011",
        "description": "Club admin fetches any application",
        "api": "GET /api/applications/{application_id}",
        "inputs": "admin token",
        "expected": _out(
            "Status: 200 OK",
        ),
    },
    "test_get_application_as_other_student": {
        "id": "APP-012",
        "description": "Another student cannot read the application",
        "api": "GET /api/applications/{application_id}",
        "inputs": "other student token",
        "expected": _out(
            "Status: 403 Forbidden",
        ),
    },
    "test_get_application_not_found": {
        "id": "APP-013",
        "description": "Fetch a non-existent application",
        "api": "GET /api/applications/{application_id}",
        "inputs": "00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Application not found",
        ),
    },
    "test_get_application_unauthenticated": {
        "id": "APP-014",
        "description": "Fetch an application without a token",
        "api": "GET /api/applications/{application_id}",
        "inputs": "no auth header",
        "expected": _out(
            "Status: 401 Unauthorized",
        ),
    },
    "test_update_application_status_accepted": {
        "id": "APP-015",
        "description": "Admin accepts a pending application",
        "api": "PATCH /api/applications/{application_id}",
        "inputs": "status='accepted'",
        "expected": _out(
            "Status: 200 OK",
            "status: 'accepted'",
        ),
    },
    "test_update_application_status_rejected": {
        "id": "APP-016",
        "description": "Admin rejects an application",
        "api": "PATCH /api/applications/{application_id}",
        "inputs": "status='rejected'",
        "expected": _out(
            "Status: 200 OK",
            "status: 'rejected'",
        ),
    },
    "test_update_application_as_student_forbidden": {
        "id": "APP-017",
        "description": "Student cannot change their own status",
        "api": "PATCH /api/applications/{application_id}",
        "inputs": "student token, status='rejected'",
        "expected": _out(
            "Status: 403 Forbidden",
        ),
    },
    "test_update_application_not_found": {
        "id": "APP-018",
        "description": "Update a non-existent application",
        "api": "PATCH /api/applications/{application_id}",
        "inputs": "00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Application not found",
        ),
    },
    "test_update_application_extra_field_rejected": {
        "id": "APP-019",
        "description": "Updates accept only status; other fields rejected",
        "api": "PATCH /api/applications/{application_id}",
        "inputs": "status + availability",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_update_application_seat_limit_conflict": {
        "id": "APP-020",
        "description": "Accepting past the seat limit is a conflict",
        "api": "PATCH /api/applications/{application_id}",
        "inputs": "bounty seat_limit=1, two applications",
        "expected": _out(
            "First: 200 OK",
            "Second: 409 Conflict",
            "Message: All seats for this bounty are filled",
        ),
    },
    "test_reaccepting_application_does_not_consume_another_seat": {
        "id": "APP-021",
        "description": "Re-accepting an accepted application is idempotent",
        "api": "PATCH /api/applications/{application_id}",
        "inputs": "accept an already-accepted application (seat_limit=1)",
        "expected": _out(
            "Status: 200 OK",
        ),
    },
    "test_delete_rejected_application_success": {
        "id": "APP-022",
        "description": "Student deletes their own rejected application",
        "api": "DELETE /api/applications/{application_id}",
        "inputs": "rejected application",
        "expected": _out(
            "Status: 204 No Content",
            "row removed",
        ),
    },
    "test_delete_pending_application_conflict": {
        "id": "APP-023",
        "description": "Only rejected applications can be deleted",
        "api": "DELETE /api/applications/{application_id}",
        "inputs": "pending application",
        "expected": _out(
            "Status: 409 Conflict",
            "Message: Only a rejected application can be deleted",
        ),
    },
    "test_delete_other_students_application_forbidden": {
        "id": "APP-024",
        "description": "Another student cannot delete the application",
        "api": "DELETE /api/applications/{application_id}",
        "inputs": "other student token",
        "expected": _out(
            "Status: 403 Forbidden",
        ),
    },
    "test_delete_application_as_admin_forbidden": {
        "id": "APP-025",
        "description": "Club admin cannot delete an application",
        "api": "DELETE /api/applications/{application_id}",
        "inputs": "admin token",
        "expected": _out(
            "Status: 403 Forbidden",
        ),
    },
    "test_delete_application_not_found": {
        "id": "APP-026",
        "description": "Delete a non-existent application",
        "api": "DELETE /api/applications/{application_id}",
        "inputs": "00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Application not found",
        ),
    },
    "test_assign_work_success": {
        "id": "WRK-001",
        "description": "Admin assigns work to an accepted application",
        "api": "POST /api/applications/{application_id}/work",
        "inputs": "accepted application, work payload + 2 deliverables",
        "expected": _out(
            "Status: 201 Created",
            "status: 'assigned'",
            "application.status: 'accepted'",
            "deliverables all 'pending'",
        ),
    },
    "test_assign_work_to_pending_application": {
        "id": "WRK-002",
        "description": "Pending application cannot receive work",
        "api": "POST /api/applications/{application_id}/work",
        "inputs": "pending application",
        "expected": _out(
            "Status: 409 Conflict",
            "Message: Only an accepted application can receive work",
        ),
    },
    "test_assign_work_to_rejected_application": {
        "id": "WRK-003",
        "description": "Rejected application cannot receive work",
        "api": "POST /api/applications/{application_id}/work",
        "inputs": "rejected application",
        "expected": _out(
            "Status: 409 Conflict",
        ),
    },
    "test_assign_work_already_assigned": {
        "id": "WRK-004",
        "description": "Assigning work twice is a conflict",
        "api": "POST /api/applications/{application_id}/work",
        "inputs": "assign twice",
        "expected": _out(
            "First: 201 Created",
            "Second: 409 Conflict",
            "Message: Work is already assigned to this application",
        ),
    },
    "test_assign_work_as_student_forbidden": {
        "id": "WRK-005",
        "description": "Student cannot assign work",
        "api": "POST /api/applications/{application_id}/work",
        "inputs": "student token",
        "expected": _out(
            "Status: 403 Forbidden",
        ),
    },
    "test_assign_work_application_not_found": {
        "id": "WRK-006",
        "description": "Assign work to a non-existent application",
        "api": "POST /api/applications/{application_id}/work",
        "inputs": "00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Application not found",
        ),
    },
    "test_assign_work_event_not_found": {
        "id": "WRK-007",
        "description": "Assign work referencing a missing event",
        "api": "POST /api/applications/{application_id}/work",
        "inputs": "event_id=00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Event not found",
        ),
    },
    "test_get_assigned_work_as_owner": {
        "id": "WRK-008",
        "description": "Student fetches their assigned work",
        "api": "GET /api/applications/{application_id}/work",
        "inputs": "student token",
        "expected": _out(
            "Status: 200 OK",
            "application_id: <application id>",
            "deliverables: 2",
        ),
    },
    "test_get_assigned_work_as_admin": {
        "id": "WRK-009",
        "description": "Club admin fetches assigned work",
        "api": "GET /api/applications/{application_id}/work",
        "inputs": "admin token",
        "expected": _out(
            "Status: 200 OK",
        ),
    },
    "test_get_assigned_work_as_other_student": {
        "id": "WRK-010",
        "description": "Another student cannot read the work",
        "api": "GET /api/applications/{application_id}/work",
        "inputs": "other student token",
        "expected": _out(
            "Status: 403 Forbidden",
        ),
    },
    "test_get_assigned_work_not_assigned": {
        "id": "WRK-011",
        "description": "No work row for the application",
        "api": "GET /api/applications/{application_id}/work",
        "inputs": "accepted application with no work",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Work not found for this application",
        ),
    },
    "test_get_assigned_work_application_not_found": {
        "id": "WRK-012",
        "description": "Fetch work for a non-existent application",
        "api": "GET /api/applications/{application_id}/work",
        "inputs": "00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Application not found",
        ),
    },
    "test_student_updates_work_status": {
        "id": "WRK-013",
        "description": "Student moves work to in_progress",
        "api": "PATCH /api/applications/{application_id}/work",
        "inputs": "status='in_progress'",
        "expected": _out(
            "Status: 200 OK",
            "status: 'in_progress'",
        ),
    },
    "test_student_updates_deliverable_status": {
        "id": "WRK-014",
        "description": "Student marks a deliverable completed",
        "api": "PATCH /api/applications/{application_id}/work",
        "inputs": "deliverable id + status='completed'",
        "expected": _out(
            "Status: 200 OK",
            "deliverable status: 'completed'",
        ),
    },
    "test_student_cannot_update_title": {
        "id": "WRK-015",
        "description": "Student cannot edit admin-only work fields",
        "api": "PATCH /api/applications/{application_id}/work",
        "inputs": "title='Hacked'",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_admin_updates_work_details": {
        "id": "WRK-016",
        "description": "Admin edits work title, description, deadline, status",
        "api": "PATCH /api/applications/{application_id}/work",
        "inputs": "title/task_description/deadline/status",
        "expected": _out(
            "Status: 200 OK",
            "title: 'Redesign'",
            "status: 'in_progress'",
        ),
    },
    "test_admin_updates_deliverable_status": {
        "id": "WRK-017",
        "description": "Admin updates a deliverable status",
        "api": "PATCH /api/applications/{application_id}/work",
        "inputs": "deliverable id + status='in_progress'",
        "expected": _out(
            "Status: 200 OK",
            "deliverable status: 'in_progress'",
        ),
    },
    "test_admin_cannot_change_application_id": {
        "id": "WRK-018",
        "description": "application_id is immutable",
        "api": "PATCH /api/applications/{application_id}/work",
        "inputs": "application_id=<other uuid>",
        "expected": _out(
            "Status: 422 Unprocessable Entity",
        ),
    },
    "test_admin_updates_event_id": {
        "id": "WRK-019",
        "description": "Admin links work to an event",
        "api": "PATCH /api/applications/{application_id}/work",
        "inputs": "valid event id",
        "expected": _out(
            "Status: 200 OK",
            "event.name: 'Hackathon'",
        ),
    },
    "test_admin_invalid_event_not_found": {
        "id": "WRK-020",
        "description": "Linking a missing event is a 404",
        "api": "PATCH /api/applications/{application_id}/work",
        "inputs": "event_id=00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Event not found",
        ),
    },
    "test_other_student_update_forbidden": {
        "id": "WRK-021",
        "description": "Another student cannot update the work",
        "api": "PATCH /api/applications/{application_id}/work",
        "inputs": "other student token",
        "expected": _out(
            "Status: 403 Forbidden",
        ),
    },
    "test_update_work_unknown_deliverable": {
        "id": "WRK-022",
        "description": "Updating a deliverable that does not belong to the work",
        "api": "PATCH /api/applications/{application_id}/work",
        "inputs": "deliverable id=00000000-0000-0000-0000-000000000000",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Deliverable not found",
        ),
    },
    "test_get_my_skills_success": {
        "id": "SKY-001",
        "description": "Student fetches their skills grouped by domain",
        "api": "GET /api/students/me/skills",
        "inputs": "student with WEB_DEVELOPMENT, REACT + NODE_JS",
        "expected": _out(
            "Status: 200 OK",
            "domain: WEB_DEVELOPMENT",
            "technologies: REACT, NODE_JS",
        ),
    },
    "test_get_my_skills_success_with_multiple_domains": {
        "id": "SKY-002",
        "description": "Skills across two domains",
        "api": "GET /api/students/me/skills",
        "inputs": "WEB_DEVELOPMENT/REACT + AI_ML/PYTORCH",
        "expected": _out(
            "Status: 200 OK",
            "2 domains: WEB_DEVELOPMENT, AI_ML",
        ),
    },
    "test_get_my_skills_empty": {
        "id": "SKY-003",
        "description": "Student with no skills returns an empty list",
        "api": "GET /api/students/me/skills",
        "inputs": "student with a profile but no skills",
        "expected": _out(
            "Status: 200 OK",
            "body: []",
        ),
    },
    "test_get_my_skills_no_profile": {
        "id": "SKY-004",
        "description": "Student without a profile cannot fetch skills",
        "api": "GET /api/students/me/skills",
        "inputs": "student user with no Student row",
        "expected": _out(
            "Status: 404 Not Found",
            "Message: Student profile not found",
        ),
    },
    "test_get_my_skills_as_admin_forbidden": {
        "id": "SKY-005",
        "description": "Club admin cannot fetch student skills",
        "api": "GET /api/students/me/skills",
        "inputs": "admin token",
        "expected": _out(
            "Status: 403 Forbidden",
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


def _load_actuals() -> dict[str, str]:
    """Map test function name -> recorded actual output text."""
    if not ACTUAL_LOG.exists():
        return {}
    return json.loads(ACTUAL_LOG.read_text(encoding="utf-8"))


def generate() -> str:
    """Build the markdown matrix document."""
    implemented = _implemented_tests()
    results = _load_results()
    actuals = _load_actuals()

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
        intentional = func in INTENTIONAL_BUG_TESTS
        if func in actuals:
            actual = actuals[func].replace("\n", " — ")
        else:
            actual = meta["expected"] if outcome == "passed" else _actual_outcome(
                outcome, intentional=intentional
            )
        result = _result(outcome, intentional=intentional)
        lines.append(
            f"| {meta['id']} | {meta['description']} | `{meta['api']}` | "
            f"{meta['inputs']} | {meta['expected']} | {actual} | {result} |"
        )

    lines.append("")
    return "\n".join(lines)


def _latest_outcome(results: dict[str, str], func: str) -> str | None:
    """Outcome of the most recent run of ``func``.

    For parametrized tests the function name is a prefix of every node id
    (``test_foo[case0]``); the most severe outcome across all cases wins so a
    single failing case is not hidden behind passing ones.
    """
    outcomes = [res for node, res in results.items() if node.rsplit("::", 1)[-1].startswith(func)]
    if not outcomes:
        return None
    if "failed" in outcomes:
        return "failed"
    if "passed" in outcomes:
        return "passed"
    return outcomes[0]


# Tests that deliberately fail while an intentional production defect is
# present. They are expected to fail and are labelled accordingly in the
# report rather than as ordinary regressions.
INTENTIONAL_BUG_TESTS: set[str] = {
    "test_create_registration_rejects_unexpected_field",  # Bug 1
    "test_update_registration_rejects_protected_fields",  # Bug 2
    "test_create_registration_duplicate_conflict",        # Bug 3
    "test_declare_winner_for_registration_of_event",      # Bug 4
    "test_generate_certificates_skips_existing",          # Bug 5
}


def _actual_outcome(outcome: str | None, *, intentional: bool = False) -> str:
    """Build the 'Actual Output' cell for a non-passing test."""
    if outcome == "failed":
        if intentional:
            return _out("Test failed (Intentional Bug) - see pytest output")
        return _out("Test failed - see pytest output")
    return _out("Not run yet")


def _result(outcome: str | None, *, intentional: bool = False) -> str:
    """Result column value."""
    if outcome == "passed":
        return "✅ Passed (Bug Fixed)" if intentional else "Success"
    if outcome == "failed":
        return "❌ Failed (Intentional Bug)" if intentional else "Fail"
    return "Not Run"


def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(generate(), encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()