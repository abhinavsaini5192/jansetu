# JanSetu Backend (Phases 1 & 2.1–2.5)

JanSetu is an AI-ready Societal Innovation and Collaboration Platform connecting citizens, communities, government departments, universities, researchers, students, industries, startups, NGOs, and CSR organizations.

---

## Technology Stack

- **Python**: 3.11+ (Tested on Python 3.14)
- **Framework**: FastAPI
- **Server**: Uvicorn
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL (with psycopg2-binary, resilient engine pooling)
- **Validation & Settings**: Pydantic v2 & Pydantic-Settings
- **Security**: JWT & Passlib (bcrypt)
- **Migrations**: Alembic

---

## Directory Structure

```text
jansetu-backend/
├── alembic/                     # Database migration management
│   ├── versions/                # Migration revision scripts
│   │   ├── 0001_initial_baseline.py
│   │   ├── 0002_create_users_table.py
│   │   ├── 0003_add_organizations_and_memberships.py
│   │   ├── 0004_create_challenges_table.py
│   │   ├── 0005_create_attachments_table.py
│   │   ├── 0006_create_government_reviews_table.py
│   │   ├── 0007_create_notifications_table.py
│   │   ├── 0008_create_audit_logs_table.py
│   │   ├── 0009_create_institutional_collaboration_tables.py # (Phases 2.1 to 2.5)
│   │   └── .gitkeep
│   ├── env.py                   # Migration environment (loads config & Base.metadata)
│   └── script.py.mako           # Migration script template
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application factory & lifecycle
│   ├── core/                    # Infrastructure, config, & security
│   │   ├── __init__.py
│   │   ├── config.py            # Environment settings & URL masking
│   │   ├── database.py          # SQLAlchemy 2.0 engine, pool config, SessionLocal, Base
│   │   ├── dependencies.py      # Dependency injection (get_db, auth, org RBAC)
│   │   ├── exceptions.py        # Global error handlers & standard error envelope
│   │   ├── logging_config.py    # Structured logging configuration
│   │   └── security.py          # Bcrypt password hashing & JWT token management
│   ├── api/                     # Versioned routing layer
│   │   ├── __init__.py
│   │   ├── router.py            # Master API router (Phase 1 & Phase 2 mounted)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── assignments.py   # Mandate assignments, accept, decline, cancel (Phase 2.4)
│   │       ├── attachments.py   # Challenge file upload, list, download, delete (Phase 1.8)
│   │       ├── audit_logs.py    # Immutable system audit trails (Phase 1.10)
│   │       ├── auth.py          # User registration, login, profile, & logout
│   │       ├── challenges.py    # Challenge CRUD endpoints (Phase 1.7)
│   │       ├── dashboard.py     # Platform metrics & summary aggregations (Phase 1.11)
│   │       ├── departments.py   # Academic departments & capabilities CRUD (Phase 2.2)
│   │       ├── government.py    # Review queue, validation, decisions, history (Phase 1.9)
│   │       ├── matching.py      # Explainable rule-based university matching (Phase 2.3)
│   │       ├── notifications.py # In-app notification alerts & read flags (Phase 1.10)
│   │       ├── organizations.py # Organizations & memberships CRUD / RBAC
│   │       ├── projects.py      # Collaborative project workspaces CRUD (Phase 2.5)
│   │       ├── system.py        # /health and /system/status endpoints
│   │       └── universities.py  # University directory & profiles (Phase 2.1)
│   ├── models/                  # SQLAlchemy ORM models package
│   │   ├── __init__.py
│   │   ├── attachment.py        # File attachment metadata entity model (Phase 1.8)
│   │   ├── audit_log.py         # Immutable audit record model (Phase 1.10)
│   │   ├── base.py              # Shared Declarative Base re-export
│   │   ├── capability.py        # Standardized research/lab capability tags (Phase 2.2)
│   │   ├── challenge.py         # Societal challenge entity model (Phase 1.6)
│   │   ├── challenge_assignment.py # Mandate invitation/assignment model (Phase 2.4)
│   │   ├── department.py        # Academic department model (Phase 2.2)
│   │   ├── department_capability.py # Department-Capability association table (Phase 2.2)
│   │   ├── government_review.py # Official review decision model (Phase 1.9)
│   │   ├── notification.py      # In-app user notification model (Phase 1.10)
│   │   ├── organization.py      # Organization entity model
│   │   ├── organization_membership.py # User-Organization association model
│   │   ├── project.py           # Institutional project workspace model (Phase 2.5)
│   │   ├── university_profile.py# Extended HEI profile entity model (Phase 2.1)
│   │   └── user.py              # User entity model (UUID, email UK, role, memberships)
│   ├── schemas/                 # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── assignment.py        # Assignment create, accept, decline, cancel schemas (Phase 2.4)
│   │   ├── attachment.py        # Attachment response and list schemas (Phase 1.8)
│   │   ├── audit_log.py         # Audit log query and item schemas (Phase 1.10)
│   │   ├── auth.py              # UserRegisterRequest, UserLoginRequest, TokenResponse
│   │   ├── challenge.py         # Challenge intake, update, and response schemas (Phase 1.6)
│   │   ├── common.py            # ApiResponse, PaginatedResponse, and System schemas
│   │   ├── dashboard.py         # Metrics, district/domain summaries, activity (Phase 1.11)
│   │   ├── department.py        # Department & Capability request/response schemas (Phase 2.2)
│   │   ├── government.py        # Decisions, review detail, and history schemas (Phase 1.9)
│   │   ├── matching.py          # Explainable match result & score breakdown schemas (Phase 2.3)
│   │   ├── notification.py      # User notifications, unread count schemas (Phase 1.10)
│   │   ├── organization.py      # Organization & Membership request/response schemas
│   │   ├── project.py           # Project create, update, and response schemas (Phase 2.5)
│   │   ├── university.py        # University profile request/response schemas (Phase 2.1)
│   │   └── user.py              # UserBase, UserResponse
│   ├── services/                # Business logic workflows
│   │   ├── __init__.py
│   │   ├── assignment_service.py# Challenge assignment state machine & notifications (Phase 2.4)
│   │   ├── attachment_service.py# Attachment upload, storage, & download service (Phase 1.8)
│   │   ├── audit_service.py     # Centralized audit logging & credential redaction (Phase 1.10)
│   │   ├── auth_service.py      # Registration & authentication workflow
│   │   ├── challenge_service.py # Challenge CRUD service (Phase 1.7)
│   │   ├── dashboard_service.py # Real SQL aggregations for overview, districts, domains (Phase 1.11)
│   │   ├── department_service.py# Department & Capability management service (Phase 2.2)
│   │   ├── government_service.py# Review queue, state machine, and decisions (Phase 1.9)
│   │   ├── matching_service.py  # Deterministic, explainable matching engine (Phase 2.3)
│   │   ├── notification_service.py # In-app notification creation and read state (Phase 1.10)
│   │   ├── organization_service.py # Organization lifecycle & RBAC authorization
│   │   ├── project_service.py   # Project workspace lifecycle & access control (Phase 2.5)
│   │   └── university_service.py# University directory & accreditation service (Phase 2.1)
│   ├── utils/                   # Enums, helpers, pagination
│   │   ├── __init__.py
│   │   ├── constants.py         # Jharkhand districts & platform limits
│   │   └── enums.py             # Enums: InstitutionCategory, AssignmentStatus, ProjectStatus
│   └── seed/                    # Administrative seeding scripts
├── uploads/                     # Storage directory for attachments (.gitkeep preserved)
│   └── challenges/              # Subdirectory for challenge file attachments (Phase 1.8)
├── tests/
│   ├── conftest.py              # TestClient fixture & isolated test database
│   ├── test_attachments.py      # Phase 1.8 attachment upload, security, and lifecycle tests
│   ├── test_auth.py             # Phase 1.4 registration, login, JWT, & security tests
│   ├── test_challenges.py       # Phase 1.6 challenge model & schema tests
│   ├── test_challenge_crud.py   # Phase 1.7 challenge CRUD API tests
│   ├── test_database.py         # Phase 1.2 database, engine, session, & Alembic tests
│   ├── test_enums.py            # Phase 1.3 centralized enums & constants tests
│   ├── test_health.py           # Phase 1.1 health, status, CORS, and error tests
│   ├── test_organizations.py   # Phase 1.5 organizations & role management tests
│   ├── test_phase1_governance.py # Phases 1.8-1.11 end-to-end governance workflow tests
│   └── test_phase2_institutional.py # Phases 2.1-2.5 institutional collaboration tests
│   ├── test_organizations.py    # Phase 1.5 organization CRUD & membership RBAC tests
│   └── test_phase1_governance.py# Phases 1.9-1.11 government workflow, notifications, audit & dashboard tests
├── .env                         # Active environment variables
├── .env.example                 # Example environment template
├── .gitignore                   # Git exclusions
├── alembic.ini                  # Alembic CLI configuration
├── requirements.txt             # Production & development dependencies
├── run.py                       # Development server runner
└── README.md                    # Setup and execution guide
```

---

## Database Setup & Configuration

### 1. PostgreSQL Prerequisites

Ensure PostgreSQL (v14+) is installed and running on your host or in Docker.

Create the platform database:
```sql
-- Connect to PostgreSQL CLI (psql)
CREATE DATABASE jansetu;
CREATE USER postgres WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE jansetu TO postgres;
```

### 2. Configure Environment (`.env`)

Verify or customize `.env`:
```env
# Database Connection (PostgreSQL primary)
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/jansetu

# Connection Pool Settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
DB_ECHO=false

# Optional individual DB parameters (if DATABASE_URL is omitted):
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=jansetu
# DB_USER=postgres
# DB_PASSWORD=password
```

> **Security Note**: `settings.masked_database_url` ensures that database passwords are never printed or leaked in application logs or API error responses.

---

## Alembic Migration Workflow

All migration commands must be run from the `jansetu-backend` directory:

### View Migration History
```powershell
python -m alembic history
```

### View Current Applied Migration
```powershell
python -m alembic current
```

### Create a New Migration (Autogenerate from Models)
```powershell
python -m alembic revision --autogenerate -m "create entity tables"
```

### Apply Migrations to Database (Upgrade to Head)
```powershell
python -m alembic upgrade head
```

### Rollback the Most Recent Migration
```powershell
python -m alembic downgrade -1
```

### Generate Static SQL (Offline Mode)
Generates SQL DDL statements without requiring an active PostgreSQL connection:
```powershell
python -m alembic upgrade head --sql
```

---

## Centralized Enums & System Constants (Phase 1.3)

All system enums and platform constants are centralized in `app/utils/enums.py` and `app/utils/constants.py` to prevent scattered string literals across routes, models, and schemas.

### Primary Enum Classes

| Enum | Location | Values | Purpose |
| :--- | :--- | :--- | :--- |
| `UserRole` | `app.utils.enums` | `citizen`, `community_organization`, `government_admin`, `district_nodal_officer`, `university_admin`, `faculty`, `student`, `researcher`, `industry_partner`, `csr_partner`, `platform_admin` | RBAC access control tiers |
| `OrganizationType` | `app.utils.enums` | `government`, `university`, `industry`, `ngo`, `community`, `research_lab`, `startup` | External institutional categories |
| `ChallengeStatus` | `app.utils.enums` | `submitted`, `under_review`, `validated`, `rejected`, `duplicate`, `needs_clarification`, `assigned` | Public governance lifecycle |
| `ValidationStatus` | `app.utils.enums` | `pending`, `validated`, `rejected`, `duplicate`, `needs_clarification` | Review outcome states |
| `PriorityLevel` | `app.utils.enums` | `low`, `medium`, `high`, `critical` | Administrative priority |
| `UrgencyLevel` | `app.utils.enums` | `low`, `medium`, `high`, `critical` | Citizen-reported urgency |
| `NotificationType` | `app.utils.enums` | `challenge_submitted`, `challenge_validated`, `challenge_rejected`, `challenge_marked_duplicate`, `clarification_requested`, `department_assigned`, `system`, `security`, `general` | User alert categories |
| `AuditAction` | `app.utils.enums` | `create`, `read`, `update`, `delete`, `login`, `logout`, `register`, `submit`, `validate`, `reject`, `mark_duplicate`, `request_clarification`, `assign_department`, `upload`, `download`, `status_change` | Immutable audit log events |
| `SocietalDomain` | `app.utils.enums` | `education`, `healthcare`, `agriculture`, `water`, `sanitation`, `environment`, `employment`, `livelihood`, `infrastructure`, `transportation`, `public_safety`, `women_child_welfare`, `tribal_welfare`, `rural_development`, `urban_development`, `digital_inclusion`, `energy`, `governance`, `accessibility`, `other` | Sectoral categorization |

### Jharkhand Districts & Validation

The 24 official districts of Jharkhand are maintained as an immutable constant:
```python
from app.utils.constants import JHARKHAND_DISTRICTS, is_valid_district, get_canonical_district

# Verification
is_valid_district("Ranchi")          # Returns: True
is_valid_district("gumla")           # Returns: True (case-insensitive)
is_valid_district("Patna")           # Returns: False

# Normalization
get_canonical_district("ranchi")     # Returns: "Ranchi"
```

### Developer Contract Rules
1. **Never use raw strings for lifecycle statuses or roles**: Always import the corresponding enum (`from app.utils.enums import ChallengeStatus, UserRole`).
2. **Enums are database & API contracts**: Enum string values must remain stable, lowercase, and snake_case for seamless serialization with Pydantic v2 and PostgreSQL.

---

## Authentication & User Management (Phase 1.4)

JanSetu utilizes cryptographic JWT access tokens and salted bcrypt password hashing for secure, stateless authentication.

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new citizen, faculty, or community account | No |
| `POST` | `/api/v1/auth/login` | Authenticate with email/password and receive Bearer JWT | No |
| `GET` | `/api/v1/auth/me` | Retrieve authenticated user profile | Yes (Bearer Token) |
| `POST` | `/api/v1/auth/logout` | Client session termination | No |

### Usage Examples

#### 1. Register a Citizen
```powershell
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{"full_name": "Ramesh Kumar", "email": "ramesh.kumar@example.com", "password": "SecurePassword123!"}'
```
Response:
```json
{
  "id": "e7c4f691-8e01-443b-871d-556157a92b23",
  "full_name": "Ramesh Kumar",
  "email": "ramesh.kumar@example.com",
  "role": "citizen",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-09-18T00:00:00Z",
  "last_login_at": null
}
```

#### 2. User Login
```powershell
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email": "ramesh.kumar@example.com", "password": "SecurePassword123!"}'
```
Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": "e7c4f691-8e01-443b-871d-556157a92b23",
    "full_name": "Ramesh Kumar",
    "email": "ramesh.kumar@example.com",
    "role": "citizen"
  },
  "expires_in": 3600
}
```

#### 3. Fetch Current Profile
```powershell
curl -X GET http://localhost:8000/api/v1/auth/me `
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsIn..."
```

### Security Architecture & Frontend Compatibility
- **Bcrypt Salt Rounds**: 12 rounds with dynamic random salt generation per password. Plain passwords and hashes are never returned by any endpoint.
- **Role Isolation**: Self-registration for administrative roles (`platform_admin`, `government_admin`, `district_nodal_officer`) is blocked at schema validation level.
- **Frontend Session Alignment**: The login response includes both `token` and `access_token` plus nested `user` properties, matching the existing `src/services/authService.js` client contract without frontend modifications.

---

## Phase 1.5: Organizations & Role Management

### Overview
JanSetu enables institutional collaboration across government departments, academic universities, research labs, startups, community bodies, and NGOs. Institutions are modeled with PostgreSQL integrity constraints, unique naming, district validation against official Jharkhand geography, and multi-tenant role-based access control (RBAC).

### Data Models

#### Organization Model (`app/models/organization.py`)
- **`id`**: String(36) UUID primary key
- **`name`**: String(255) Unique organization name (case-insensitive deduplication)
- **`legal_name`**: Optional registered corporate or trust title
- **`organization_type`**: `OrganizationType` enum (`government`, `university`, `industry`, `ngo`, `community`, `research_lab`, `startup`)
- **`district`**: Standardized Jharkhand administrative district (validated against 24 official districts)
- **`state`**: Default `"Jharkhand"`
- **`is_active`** / **`is_verified`**: Operational and governance verification flags
- **`created_at`** / **`updated_at`**: Timezone-aware UTC timestamps
- **`memberships`**: One-to-many relationship with cascade delete to memberships (protecting users from deletion)

#### Organization Membership Model (`app/models/organization_membership.py`)
- **`id`**: String(36) UUID primary key
- **`user_id`**: Foreign key to `users.id` (ondelete="CASCADE")
- **`organization_id`**: Foreign key to `organizations.id` (ondelete="CASCADE")
- **`membership_role`**: `OrganizationMembershipRole` enum (`owner`, `admin`, `member`)
- **`is_active`**: Membership activity state
- **`joined_at`**: Timestamp of enrollment
- **`uq_user_organization_membership`**: Unique constraint on `(user_id, organization_id)`

### Platform Roles vs Organization Roles
| Role Scope | Enum | Responsibility | Example |
| :--- | :--- | :--- | :--- |
| **Global Platform Role** | `UserRole` | Determines global authority and cross-platform privileges | `PLATFORM_ADMIN`, `GOVERNMENT_ADMIN`, `CITIZEN` |
| **Organization Membership Role** | `OrganizationMembershipRole` | Governs access within a single specific institution | `OWNER`, `ADMIN`, `MEMBER` |

> [!IMPORTANT]
> An organization membership role (e.g. `OWNER`) never elevates a user's global platform role. A citizen who creates a startup becomes the `OWNER` of that startup while remaining a `CITIZEN` globally.

### Institutional Authorization Rules
1. **Creation Control**: Citizens and general users cannot freely register privileged entities (`government`, `university`) without official administrative authorization.
2. **Automatic Ownership**: The authenticated creator of an organization is automatically assigned the initial `OWNER` membership.
3. **Institutional Administration**: Only organization `OWNER`s, `ADMIN`s, or global `PLATFORM_ADMIN`s can update organization profiles or manage members.
4. **Sole Owner Protection**: The sole active owner of an organization cannot be removed, deactivated, or demoted without first designating another owner.

### Organization API Endpoints

| Endpoint | Method | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `/api/v1/organizations` | `GET` | Public | Paginated listing with filters (`type`, `district`, `is_active`, `search`) |
| `/api/v1/organizations` | `POST` | Authenticated | Register organization (creator enrolled as `OWNER`) |
| `/api/v1/organizations/{organization_id}` | `GET` | Public | Fetch organization profile by ID |
| `/api/v1/organizations/{organization_id}` | `PATCH` | Owner / Admin / Platform Admin | Update organization details |
| `/api/v1/organizations/{organization_id}/members` | `GET` | Public | List enrolled members |
| `/api/v1/organizations/{organization_id}/members` | `POST` | Owner / Admin / Platform Admin | Enroll existing user as member |
| `/api/v1/organizations/{organization_id}/members/{user_id}` | `PATCH` | Owner / Admin / Platform Admin | Promote/demote member or toggle active status |
| `/api/v1/organizations/{organization_id}/members/{user_id}` | `DELETE` | Owner / Admin / Self / Platform Admin | Remove member (protects sole owner) |

### Example Organization API Usage

#### Create Organization
```powershell
curl -X POST http://localhost:8000/api/v1/organizations `
  -H "Authorization: Bearer <TOKEN>" `
  -H "Content-Type: application/json" `
  -d '{
    "name": "Ranchi Agro Innovation Foundation",
    "organization_type": "startup",
    "district": "Ranchi",
    "state": "Jharkhand",
    "description": "Smart agriculture solutions for tribal farmers."
  }'
```

#### Add Organization Member
```powershell
curl -X POST http://localhost:8000/api/v1/organizations/<ORG_ID>/members `
  -H "Authorization: Bearer <TOKEN>" `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": "<USER_ID>",
    "membership_role": "admin"
  }'
```

---

## Phase 1.6 — Challenge Models & Schemas (Completed)

Phase 1.6 establishes the foundational database model, Pydantic v2 validation schemas, human-readable reference codes, and repository persistence layer for societal challenges.

### 1. Challenge Model Purpose
A challenge represents a real-world community or grassroots societal problem submitted by citizens, community organizations, NGOs, or authorized actors across Jharkhand's 24 administrative districts. It captures structured information required for subsequent government nodal verification, AI duplicate clustering, and university project matchmaking.

### 2. Main Challenge Fields

| Category | Field | Type | Description / Constraints |
| :--- | :--- | :--- | :--- |
| **Identity** | `id` | `String(36)` | Unique UUID primary key (indexed) |
| | `reference_code` | `String(32)` | Server-generated human-readable code: `JS-YYYY-XXXXXX` (unique, indexed) |
| **Submitter** | `submitted_by_user_id` | `String(36)` | Submitting User FK (`ondelete="RESTRICT"`, indexed) |
| | `submitted_by_organization_id` | `String(36)` | Optional Submitting Organization FK (`ondelete="SET NULL"`, indexed) |
| **Core Information** | `title` | `String(255)` | Challenge title (min 5 characters) |
| | `title_hi` | `String(255)` | Hindi title translation (optional) |
| | `description` | `Text` | Detailed problem statement (min 10 characters) |
| | `problem_statement` | `Text` | Structured breakdown of the issue |
| | `proposed_context` | `Text` | Environmental, seasonal, or historical context |
| **Location** | `district` | `String(100)` | Official Jharkhand district (indexed, validated against 24 districts) |
| | `block` | `String(100)` | Administrative block/tehsil |
| | `village_or_ward` | `String(100)` | Gram panchayat, village, or urban ward |
| | `location_description` | `String(500)` | Landmarks, GPS context, or transit details |
| **Classification** | `domain` | `String(50)` | Centralized `SocietalDomain` enum value (indexed) |
| | `subdomain` | `String(100)` | Granular sub-sector classification |
| | `priority` | `String(50)` | `PriorityLevel` enum (`low`, `medium`, `high`, `critical`) |
| | `urgency` | `String(50)` | `UrgencyLevel` enum (`low`, `medium`, `high`, `critical`) |
| **Workflow** | `status` | `String(50)` | Platform status (default: `submitted`, indexed) |
| | `validation_status` | `String(50)` | Government review status (default: `pending`, indexed) |
| | `assigned_department` | `String(255)` | Nodal government department assigned |
| **Impact & Context** | `affected_population` | `String(255)` | Community demographic affected |
| | `estimated_beneficiaries` | `Integer` | Numerical count of impacted citizens |
| | `existing_attempts` | `Text` | Past community interventions or failed remedies |
| | `expected_outcome` | `Text` | Targeted societal outcome |
| | `constraints` | `Text` | Logistical, topographic, or resource limitations |
| **Timestamps** | `submitted_at` | `DateTime(tz)` | Submission timestamp |
| | `created_at` | `DateTime(tz)` | Record creation timestamp (indexed) |
| | `updated_at` | `DateTime(tz)` | Auto-updating timestamp |
| **Future Flags** | `validated_at` | `DateTime(tz)` | Nodal validation approval timestamp |
| | `rejected_at` | `DateTime(tz)` | Rejection timestamp |
| | `duplicate_of_challenge_id` | `String(36)` | Self-referential FK to parent Challenge (`ondelete="SET NULL"`) |

### 3. Challenge Lifecycle & Status Semantics

#### ChallengeStatus
- `SUBMITTED`: Newly lodged by citizen/community, awaiting initial nodal triage.
- `UNDER_REVIEW`: Actively undergoing verification and site assessment by nodal officer.
- `VALIDATED`: Certified authentic, policy-aligned, and ready for university/industry matchmaking.
- `REJECTED`: Deemed invalid, frivolous, duplicate, or non-actionable.
- `DUPLICATE`: Linked to an existing parent challenge record.
- `NEEDS_CLARIFICATION`: More evidence, location clarity, or information requested from citizen.
- `ASSIGNED`: Allocated to a higher education institution or department for solution development.

#### ValidationStatus
- `PENDING`: Initial state awaiting departmental review.
- `VALIDATED`: Approved by government nodal officer.
- `REJECTED`: Rejected during official verification.
- `DUPLICATE`: Identified as redundant by nodal officer or duplicate detection.
- `NEEDS_CLARIFICATION`: Clarification requested from citizen submitter.

### 4. Submission Ownership & Data Integrity Rules
1. **User Requirement**: A valid authenticated user must exist before submitting a challenge.
2. **Deletion Protection**: Deleting a User account is restricted if challenges are associated with them (`ondelete="RESTRICT"`).
3. **Institutional Flexibility**: The organization affiliation is optional; if an organization record is deleted, the challenge remains intact (`ondelete="SET NULL"`).
4. **System-Managed Isolation**: Clients cannot manipulate governance fields (`status`, `validation_status`, `submitted_by_user_id`, `created_at`, `submitted_at`, `assigned_department`) on creation or update.

### 5. Schema Validation & Frontend Contract Compatibility
- **Bidirectional Location Format**: Accommodates both flat fields (`district`, `block`, `village_or_ward`) and nested objects (`location: { district, block, panchayat }`) sent by frontend `2_CitizenPortal.jsx`.
- **Domain Normalization**: Seamlessly accepts canonical `SocietalDomain` values as well as frontend UI tokens (`water_sanitation` → `water`, `clean_energy` → `energy`, `smart_education` → `education`, `waste_management` → `sanitation`).
- **Urgency & Priority**: Case-insensitive normalization converts uppercase frontend values (`CRITICAL`, `HIGH`) to centralized enum members.
- **Strict String Constraints**: Rejects empty strings or whitespace-only values for `title` (min 5 chars) and `description` (min 10 chars).

### 6. Alembic Migration Instructions

To apply the challenge table migration to the database:
```powershell
# Upgrade to latest revision (creates challenges table and indexes)
alembic upgrade head

# Verify current revision
alembic current
# Output: 0004_challenges (head)

# Rollback challenge table if necessary
alembic downgrade -1
```

> [!NOTE]
> AI processing, virus scanning service, cloud storage (S3/MinIO), and government verification belong to Phase 1.9+ and are not part of Phase 1.8.

---

## Phase 1.8 — Challenge File Attachments

JanSetu allows authenticated citizens, NGOs, and community leaders to attach supporting evidence (field photographs, laboratory water reports, official petitions, and research documents) to societal challenges.

### 1. Configuration Variables

Configured in `app/core/config.py` and overridden via `.env`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `UPLOAD_DIR` | `uploads/challenges` | Filesystem storage path for uploaded challenge attachments |
| `MAX_UPLOAD_SIZE_MB` | `10` | Maximum allowable file size per upload (10 MB) |
| `ALLOWED_UPLOAD_EXTENSIONS` | `jpg,jpeg,png,webp,pdf,doc,docx` | Safe file extension whitelist |

The upload directory is automatically created upon service startup or first upload if not already present.

### 2. File Type Whitelist & Dangerous File Rejection

- **Permitted Formats**:
  - Images: `.jpg`, `.jpeg`, `.png`, `.webp`
  - Documents: `.pdf`, `.doc`, `.docx`
- **Strictly Prohibited Executable/Dangerous Extensions**:
  - Scripts & Executables: `.exe`, `.sh`, `.bat`, `.cmd`, `.js`, `.mjs`, `.php`, `.py`, `.dll`, `.vbs`, `.ps1`, `.com`, `.scr`, `.msi`, `.bin`, `.jar`
- **MIME Type Validation**: Evaluated against whitelisted MIME types (`image/jpeg`, `image/png`, `image/webp`, `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`). Dangerous MIME types are rejected with HTTP 400.

### 3. Secure File Naming & Path Traversal Prevention

- **Unique Stored Filenames**: Files on disk are named using `<uuid4>.<safe_ext>` (e.g., `4f9b8c2d1e0a4f5b8c2d1e0a4f5b8c2d.pdf`). User-supplied filenames are never used as disk paths.
- **Path Sanitization**: User original filenames are stripped of directory components (`../`, `..\`, null bytes, control characters) and stored safely in the database for client download references.
- **Storage Boundary Checks**: All destination paths are verified to reside strictly within `UPLOAD_DIR`, preventing directory traversal and path injection attacks.
- **Atomic Cleanup on DB Failure**: If physical file writing succeeds but database persistence fails, the saved physical file is immediately unlinked and removed.
- **Graceful Deletion**: Deleting an attachment deletes the database record and unlinks the physical file. If the physical file was already missing, the operation completes without error.
- **Path Shielding**: Server internal storage paths (`storage_path`) are never returned in public JSON API payloads. Public responses expose clean metadata and the relative download endpoint URL (`/api/v1/attachments/{id}/download`).

### 4. API Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/challenges/{challenge_id}/attachments` | Upload supporting file (`multipart/form-data`) | Yes (Bearer) | Challenge submitter, org member, or platform admin |
| `GET` | `/api/v1/challenges/{challenge_id}/attachments` | List all attachments for a challenge | Yes (Bearer) | Challenge submitter, org member, or platform admin |
| `GET` | `/api/v1/attachments/{attachment_id}/download` | Stream and download binary attachment file | Yes (Bearer) | Submitter, uploader, org member, or platform admin |
| `DELETE` | `/api/v1/attachments/{attachment_id}` | Delete attachment record and unlink disk file | Yes (Bearer) | Attachment uploader, challenge submitter, or admin |

### 5. Example cURL Upload Request

```bash
curl -X POST \
  http://localhost:8000/api/v1/challenges/8c1e4889-cb62-4ef9-bb6e-214472d075eb/attachments \
  -H "Authorization: Bearer <your_jwt_token>" \
  -F "file=@problem_evidence.pdf"
```

### 6. Security Limitations & S3/MinIO Migration Path

- **Current Architecture**: Uses local filesystem storage (`uploads/challenges`) for demo-readiness, zero external cloud dependencies, and fast evaluation.
- **Limitations**:
  - Not distributed across multi-node server clusters without shared network filesystems (NFS/EFS).
  - Does not execute antivirus daemon scanning (e.g., ClamAV).
  - Does not perform AI OCR or deep document inspection (deferred to Phase 1.9+).
- **Future Migration to Cloud Object Storage (S3 / MinIO / GCS)**:
  - Storage logic is encapsulated in `app/services/attachment_service.py`.
  - When migrating to S3 or MinIO, the local methods `_save_file_to_disk` and `_safe_unlink` can be replaced with `boto3.client("s3").upload_fileobj` and presigned download URL generation, leaving existing database schema, foreign keys, and REST API contracts completely intact.

---

## Phase 1.9 — Government Validation Workflow

JanSetu provides an official, human-authorized government review process where authorized nodal officers verify citizen problem statements, designate priorities, reject invalid submissions with recorded rationales, identify duplicates, or request further citizen clarification.

### 1. State Machine & Transitions

The challenge lifecycle enforces strict transitions through the `government_service`:

```text
               ┌─────────────── SUBMITTED ───────────────┐
               │                     │                   │
               ▼                     ▼                   ▼
       [UNDER_REVIEW]           [VALIDATED]         [REJECTED]*
        │      │     │                               (terminal)
        ▼      ▼     ▼
  [VALIDATED] [REJECTED]* [DUPLICATE]*
                          (terminal)
        │
        ▼
   [ASSIGNED] (e.g., department designated)
```
- **Clarification Loop**: `SUBMITTED / UNDER_REVIEW` → `NEEDS_CLARIFICATION` → `UNDER_REVIEW`.
- **Terminal States**: `REJECTED` and `DUPLICATE` are permanent terminal states and cannot be transitioned to any other status.
- **Illegal Reversals Blocked**: Reversals such as `VALIDATED` → `SUBMITTED`, `REJECTED` → `VALIDATED`, or `DUPLICATE` → `VALIDATED` are blocked with HTTP 400.

### 2. Role Permissions (RBAC)

| User Role | Can View Queue | Can Review & Validate | Can View History |
| :--- | :---: | :---: | :---: |
| `CITIZEN`, `STUDENT`, `FACULTY`, `RESEARCHER` | ❌ (403) | ❌ (403) | Own challenges only |
| `COMMUNITY_ORGANIZATION`, `INDUSTRY_PARTNER` | ❌ (403) | ❌ (403) | Own challenges only |
| `DISTRICT_NODAL_OFFICER` | ✅ | ✅ | ✅ |
| `GOVERNMENT_ADMIN` | ✅ | ✅ | ✅ |
| `PLATFORM_ADMIN` | ✅ | ✅ | ✅ |

### 3. API Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/government/challenges/pending` | Paginated queue of challenges requiring review | Yes | Government / Admin roles |
| `GET` | `/api/v1/government/validation-queue` | Frontend queue endpoint alias | Yes | Government / Admin roles |
| `GET` | `/api/v1/government/challenges/{id}` | Detailed challenge inspection view | Yes | Government / Admin roles |
| `POST` | `/api/v1/government/challenges/{id}/review` | Submit official decision (`validate`, `reject`, etc.) | Yes | Government / Admin roles |
| `GET` | `/api/v1/government/challenges/{id}/review-history` | Historical audit trail of all review cycles | Yes | Submitter / Gov / Admin |
| `POST` | `/api/v1/government/challenges/{id}/validate` | Frontend quick validation shortcut | Yes | Government / Admin roles |
| `POST` | `/api/v1/government/challenges/{id}/reject` | Frontend quick rejection shortcut | Yes | Government / Admin roles |
| `POST` | `/api/v1/government/challenges/{id}/assign-department` | Assign department to validated challenge | Yes | Government / Admin roles |
| `GET` | `/api/v1/government/departments` | List official Jharkhand government departments | Yes | Authenticated users |

### 4. Example Government Review Decision Request

```bash
curl -X POST \
  http://localhost:8000/api/v1/government/challenges/8c1e4889-cb62-4ef9-bb6e-214472d075eb/review \
  -H "Authorization: Bearer <government_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "validate",
    "review_comment": "Field inspection confirmed severe arsenic contamination. Forwarding to PHED.",
    "department": "Public Health Engineering Department (PHED)"
  }'
```

---

## Phase 1.10 — Notifications & Audit Logs

### 1. In-App Notifications

Provides persistent, non-intrusive in-app alerts delivered to citizens when administrative decisions are made on their challenges.

- **Event Triggers**:
  - Challenge submitted confirmation
  - Challenge officially validated
  - Challenge rejected (with official reason)
  - Challenge marked as duplicate (with target challenge reference)
  - Clarification requested by government official
  - Government department assigned
- **Endpoints**:
  - `GET /api/v1/notifications`: Paginated list of notifications for the authenticated user (`unread_only=true` filter supported)
  - `GET /api/v1/notifications/unread-count`: Badge counter for navbar indicators
  - `PATCH /api/v1/notifications/{id}/read`: Mark individual alert as read
  - `PATCH /api/v1/notifications/read-all` & `POST /api/v1/notifications/read-all`: Mark all notifications as read

### 2. Immutable Operational Audit Logs

Centralized, tamper-resistant logging via `audit_service.record_audit_event`:
- **Captured Events**: User registration, login, challenge creation/updates/deletions, attachment uploads/deletions, and government review decisions.
- **Security & Redaction**: Recursive metadata sanitation automatically strips and redacts passwords, JWT tokens, hashes, and secret keys (`[REDACTED]`).
- **Access Restriction**: Restricted to `PLATFORM_ADMIN` and `GOVERNMENT_ADMIN`. Ordinary users receive HTTP 403 Forbidden.
- **Endpoints**:
  - `GET /api/v1/audit-logs`: Query audit records with filters by `actor`, `action`, `entity_type`, and timestamp ranges (`from_date`, `to_date`).

```bash
curl -X GET \
  "http://localhost:8000/api/v1/audit-logs?entity_type=challenge" \
  -H "Authorization: Bearer <admin_jwt_token>"
```

---

## Phase 1.11 — Platform Dashboards & Integration

Provides aggregate statistics for executive dashboards and frontend visualizations calculated strictly using real database SQL aggregation queries (zero mock/fake data).

### 1. Available Metrics
- Challenge counts by lifecycle status (`total_challenges`, `submitted_challenges`, `under_review_challenges`, `validated_challenges`, `rejected_challenges`, `duplicate_challenges`, `clarification_needed_challenges`, `assigned_challenges`)
- Caller unread notifications count
- District distributions across Jharkhand's 24 districts with validated subcounts
- Sectoral domain distributions with localized English/Hindi labels
- Recent platform activity feed derived from audit records

### 2. API Endpoints

| Method | Endpoint | Description | Return Format |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/dashboard/overview` | Platform challenge totals & user unread counts | Object (snake_case + camelCase) |
| `GET` | `/api/v1/dashboard/stats` | Frontend stats alias for overview | Object |
| `GET` | `/api/v1/dashboard/challenges-summary` | Alternate overview alias | Object |
| `GET` | `/api/v1/dashboard/district-summary` | District breakdown with total districts | Object (`{ items: [...], total_districts }`) |
| `GET` | `/api/v1/dashboard/districts` | Frontend direct array of district counts | Array (`[ { district, count, validated_count } ]`) |
| `GET` | `/api/v1/dashboard/domain-summary` | Domain breakdown with total domains | Object (`{ items: [...], total_domains }`) |
| `GET` | `/api/v1/dashboard/domains` | Frontend direct array of domain counts | Array (`[ { domain, count, label } ]`) |
| `GET` | `/api/v1/dashboard/activity` | Recent activity timeline | Array (`[ { id, type, title, description, timestamp } ]`) |

---

---

## Phase 2: Institutional Collaboration Platform (Phases 2.1 — 2.5)

Phase 2 transforms JanSetu into an institutional collaboration platform connecting validated civic challenges with academic institutions across Jharkhand.

### Core Modules

1. **Phase 2.1 — University Directory & HEI Profiles**:
   - Extends the core `Organization` model (`organization_type = UNIVERSITY`) with a 1-to-1 `UniversityProfile` record.
   - Captures institutional code (e.g., AISHE/NIRF), NAAC/NBA accreditation details, establishment year, district, state, and verification status.
   - Public directory allows viewing verified institutions; platform admins can verify HEIs.

2. **Phase 2.2 — Academic Departments & Capabilities**:
   - `Department` entities represent academic/research divisions within an institution.
   - `Capability` models standardized skills, domain tags, and specialized laboratory infrastructure (e.g., `water-testing`, `iot-sensing`, `gis-mapping`).
   - Many-to-many association via `department_capabilities`.
   - Strictly scoped: Only institutional administrators (`university_admin`, `hei_admin`, or platform admin) can manage departments and link capabilities for their institution.

3. **Phase 2.3 — Explainable University Matching Engine**:
   - **Purely deterministic, rule-based matching** with zero machine learning, embeddings, or vector databases.
   - **Total Score (0–100 points)** calculated transparently:
     - **Domain Match (40% / 40 pts)**: Evaluates overlap between challenge domain/subdomain and departmental capability tags.
     - **Keyword Overlap (25% / 25 pts)**: Tokenizes challenge title, description, and problem statement and matches against university/department capability tokens.
     - **District Proximity (20% / 20 pts)**: Full 20 pts awarded if university and challenge reside in the same district; 5 pts baseline for intra-state.
     - **Accreditation / Type (15% / 15 pts)**: Weighted by NAAC grade (A++: 15, A+: 13, A: 11, B: 7) or institution tier (NIT/IIT/Central: 15, State Univ: 12, College: 8).
   - Only **validated challenges** (`validation_status = 'validated'`) can be matched. Non-validated challenges return HTTP 400.
   - Returns sorted candidates with complete, auditable scoring breakdowns (`domain_score`, `keyword_score`, `district_score`, `institution_type_score`, `match_reasons`).

4. **Phase 2.4 — Challenge Assignment & Acceptance Lifecycle**:
   - Government nodal officers and platform admins can formally issue mandate invitations (`ChallengeAssignment`) to matched HEIs.
   - State Machine:
     - `INVITED`: Government has issued mandate invitation. Challenge status advances to `ASSIGNED`.
     - `ACCEPTED`: Target university admin accepts invitation. Automatically transitions challenge to `ASSIGNED` and provisions project workspace.
     - `DECLINED`: Target university admin declines. If no other accepted assignments exist, challenge rolls back to `VALIDATED`.
     - `CANCELLED`: Government or platform admin revokes the invitation.
   - Duplicate active assignments (`INVITED` or `ACCEPTED`) for the same university and challenge are rejected with HTTP 409 Conflict.

5. **Phase 2.5 — Collaborative Project Workspaces**:
   - Project entity (`Project`) serves as the execution environment for accepted mandates.
   - **Idempotent Creation**: Acceptance of an assignment automatically creates or returns the unique project workspace (`PRJ-YYYY-XXXXXX`).
   - **Strict Access Control**: Only target university members, assigned faculty/students, submitter, and government/platform admins can access private project details. Cross-institution access without authorization is strictly rejected with HTTP 403 Forbidden.

### Phase 2 API Reference

| Method | Endpoint | Description | Access / RBAC |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/universities` | List active, verified universities | Public / Authenticated |
| `POST` | `/api/v1/universities` | Register university profile | University Admin / Gov / Platform Admin |
| `GET` | `/api/v1/universities/{id}` | Get university details with departments | Public / Authenticated |
| `POST` | `/api/v1/universities/{id}/verify` | Mark university as verified | Platform Admin / State Nodal Officer |
| `GET` | `/api/v1/departments` | List academic departments | Authenticated |
| `POST` | `/api/v1/departments` | Create academic department | University Admin for target HEI |
| `POST` | `/api/v1/departments/{id}/capabilities` | Associate capabilities with department | University Admin for target HEI |
| `GET` | `/api/v1/challenges/{id}/matches` | Explainable matching recommendations | Gov / Submitter / Platform Admin |
| `POST` | `/api/v1/challenges/{id}/assignments` | Issue mandate assignment | Gov Nodal Officer / Platform Admin |
| `GET` | `/api/v1/challenges/{id}/assignments` | List assignments for a challenge | Gov / Submitter / Uni Admin |
| `POST` | `/api/v1/challenges/{id}/assign-hei` | Assign HEI convenience alias | Gov Nodal Officer / Platform Admin |
| `POST` | `/api/v1/assignments/{id}/accept` | Accept mandate & initialize workspace | Target University Admin |
| `POST` | `/api/v1/assignments/{id}/decline` | Decline mandate invitation | Target University Admin |
| `POST` | `/api/v1/assignments/{id}/cancel` | Cancel mandate invitation | Gov Nodal Officer / Platform Admin |
| `GET` | `/api/v1/projects` | List visible project workspaces | Filtered by institution & role |
| `GET` | `/api/v1/projects/{id}` | Get project workspace details | Authorized project members & Gov |
| `PUT` | `/api/v1/projects/{id}` | Update progress/budget/faculty | University Admin / Assigned Lead |
| `GET` | `/api/v1/challenges/{id}/project` | Retrieve workspace by challenge | Authorized project members & Gov |

---

## Database Migrations (Phases 1.1 — 2.5)

All database schema evolutions are managed sequentially via Alembic:

| Revision ID | Description | Created Tables / Indexes |
| :--- | :--- | :--- |
| `0001_initial` | Baseline migration | None |
| `0002_users` | User management | `users` |
| `0003_organizations` | Organizations & memberships | `organizations`, `organization_memberships` |
| `0004_challenges` | Societal challenges | `challenges` |
| `0005_attachments` | File attachments (Phase 1.8) | `attachments` |
| `0006_government_reviews` | Verification workflow (Phase 1.9) | `government_reviews` |
| `0007_notifications` | In-app notifications (Phase 1.10) | `notifications` |
| `0008_audit_logs` | Immutable audit log (Phase 1.10) | `audit_logs` |
| `0009_institutional` | Institutional collaboration (Phases 2.1–2.5) | `university_profiles`, `departments`, `capabilities`, `department_capabilities`, `challenge_assignments`, `projects` |

### Applying Migrations

```powershell
# Upgrade database schema to head (0009_institutional)
alembic upgrade head

# Check current revision status
alembic current
# Expected output: 0009_institutional (head)

# Downgrade single revision if needed
alembic downgrade -1
```

---

## Current Architecture Boundaries & Limitations

1. **Storage**: Local filesystem storage (`uploads/challenges`) is currently active. Storage abstraction is ready for transparent S3/MinIO cloud migration in subsequent production deployments.
2. **Matching Engine**: Phase 2.3 uses pure rule-based deterministic scoring. No AI/ML embeddings, vector databases, or semantic similarity algorithms are used.
3. **Notifications**: Currently in-app only; email (SMTP/SES), SMS, push notifications, and WebSockets are deferred to future phases.
4. **Human Authorization**: Government decisions and institutional assignments require explicit human review by authorized officers and institutional administrators. Automated bypass is not permitted.
5. **Phase Scope Boundaries**: Advanced student/mentor task boards, multi-tier milestone approvals, field trials, CSR co-funding, and pilot deployment verification belong strictly to Phases 2.6–2.11 and Phase 3 and are not included in this release.

---

## Running the Application

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Start the Server
```powershell
python run.py
```
Or:
```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Health & Connectivity Probing

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/health` | `GET` | High-frequency container vitality probe (`{"status": "healthy", "service": "jansetu-backend"}`) |
| `/api/v1/system/status` | `GET` | Operational health probe with dynamic PostgreSQL connectivity status (`SELECT 1`) |
| `/docs` | `GET` | Interactive Swagger API documentation |

### Resilient Startup Behavior
The application starts stably even if PostgreSQL is temporarily offline or undergoing maintenance. Database-dependent operations report controlled status responses without crashing the process.

---

## Testing

Run the automated test suite with pytest:
```powershell
python -m pytest tests/ -v
```

---

## Phase 3.1 – 3.5: AI Problem Intelligence & Explainable Matching

JanSetu includes an AI Problem Intelligence and Semantic Similarity architecture designed for reliability, transparency, and government-supervised governance.

### 1. AI Configuration
Managed via environment variables (`.env`):
```ini
AI_ENABLED=false
AI_PROVIDER=none
AI_API_KEY=
AI_MODEL=
AI_TIMEOUT_SECONDS=20
```

### 2. AI Architecture & Provider Structure
The AI subsystem (`app/ai/`) follows a clean provider abstraction:
- `BaseAIProvider`: Abstract contract defining `analyze_challenge`, `classify_challenge`, `extract_entities`, and `generate_summary`.
- `DeterministicFallbackProvider`: Zero-network, rule-based inference engine utilizing regional dictionaries (24 Jharkhand districts, societal domains, stakeholder keywords, and capability matrices). Transparently reports `fallback_used: true` and `provider: "deterministic-fallback"`.
- `ExternalAIProvider`: Adapter for hosted LLMs (Gemini, OpenAI, etc.) with timeout bounds, error isolation, and credential masking.
- `AIService`: Orchestrator that attempts the active provider and seamlessly falls back to deterministic analysis upon any network error, missing key, or timeout.

### 3. AI-Disabled & Fault-Tolerant Startup Behavior
- When `AI_ENABLED=false` or no API key is provided, the backend operates in 100% deterministic fallback mode.
- Application startup never fails due to missing AI credentials or unreachable external endpoints.
- API keys are never exposed in server logs or API responses.

### 4. Semantic Similarity & Advisory Duplicate Detection
- **No Vector Database Required**: Uses localized pure-Python TF-IDF vectorization and cosine similarity ($CosineSimilarity(\vec{A}, \vec{B})$) across challenge title, description, problem statement, and expected outcomes.
- **Multi-Field Proximity**: Combines semantic text similarity (65%), societal domain matching (20%), and geographic district proximity (15%).
- **Advisory Duplicate Detection**: Derives deterministic confidence levels:
  - $\ge 75\%$: **HIGH** confidence (Flag for government review as likely duplicate or duplicate cluster)
  - $\ge 50\%$: **MEDIUM** confidence (Review for potential regional synergy or overlapping community report)
  - $< 50\%$: **LOW** confidence (Treat as distinct regional challenge)
- **No Automatic Actions**: AI recommendations are strictly advisory. The system **never** automatically deletes, merges, rejects, or marks challenges as duplicate. Government nodal officers retain sole official decision authority.

### 5. Advanced Explainable University Matching (Phase 3.5)
Pairing validated civic challenges with accredited Higher Education Institutions (HEIs) uses transparent, multi-factor scoring:
- **Scoring Breakdown (Total: 100 points)**:
  - Domain Alignment: 30 points
  - Capability Match: 30 points
  - Keyword Similarity: 15 points
  - Geographic Relevance (District Proximity): 15 points
  - Urgency & Category Readiness: 10 points
- **Explainability**: Every match returns an exact score breakdown, missing capabilities assessment, and human-verifiable rationales.
- **Non-Autonomous Mandates**: Universities are not assigned automatically; government administrators review explainable scores and issue official assignments.

### 6. Phase 3.1 – 3.5 API Endpoints

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/api/v1/ai/challenges/{id}/analyze` | `POST` | AI/fallback problem analysis, classification, and entity extraction |
| `/api/v1/challenges/{id}/ai-analysis` | `GET` | Frontend Screen 03 intelligence and duplicate cluster inspection |
| `/api/v1/challenges/{id}/ai-analysis/trigger` | `POST` | Frontend Screen 03 analysis trigger/refresh |
| `/api/v1/ai/challenges/{id}/similar` | `GET` | Top semantically similar challenges via TF-IDF cosine matching |
| `/api/v1/ai/challenges/{id}/duplicate-check` | `GET` | Advisory duplicate likelihood, confidence tier, and recommendations |
| `/api/v1/challenges/{id}/matches` | `GET` | Explainable university matching with transparent score breakdowns |

---

## Phase 3.6 – 3.11: Impact, Evidence, Analytics, Project Intelligence & Production Readiness

### 1. Phase 3.6 — Impact Management
Captures actual societal outcomes and community metrics resulting from completed projects.
- **Separation of Concerns**: Project completion does NOT automatically equal verified impact. Impact is recorded in a dedicated `ImpactRecord` entity with its own state lifecycle (`DRAFT` → `SUBMITTED` → `UNDER_REVIEW` → `VERIFIED` / `REJECTED` / `NEEDS_CLARIFICATION`).
- **Human Authority**: Government nodal officers hold sole legal authority to certify impact. Project members or submitters cannot self-verify their own impact submissions.
- **Auditing**: Every verification decision logs an immutable audit event, creates notifications, and produces project timeline activity without altering the original challenge status.

### 2. Phase 3.7 — Evidence Submission & Verification
Attaches auditable field proof to societal impact records via the unified `Attachment` system:
- **Evidence Dossiers**: Photodocumentation, drone surveys, beneficiary feedback, lab test certificates, and official government records (`EvidenceRecord`).
- **Human-Controlled Verification**: File uploads do not automatically grant verification. Evidence verification is evaluated by nodal reviewers and remains strictly human-verified.

### 3. Phase 3.8 — Analytics & Reporting
Real-time database-backed governance reporting using pure SQLAlchemy aggregation queries (`COUNT`, `SUM`, `GROUP BY`).
- **Zero Fake Data**: All numbers stem directly from active database records.
- **Graceful Empty State**: Returns structured zero counts and empty arrays when no records exist without crashing.
- **Endpoints**:
  - `GET /api/v1/analytics/overview`: Platform-wide high-level metrics (challenges, projects, universities, partners, verified impact).
  - `GET /api/v1/analytics/challenges`: Breakdown by district, domain, priority, urgency, and status.
  - `GET /api/v1/analytics/projects`: Milestone completion rates, active risks, and partnership totals.
  - `GET /api/v1/analytics/impact`: Villages covered, beneficiaries reached, and verified percentage.
  - `GET /api/v1/analytics/districts`: District-level civic metrics across Jharkhand.
  - `GET /api/v1/analytics/domains`: Sectoral domain performance.

### 4. Phase 3.9 — AI Project Intelligence
Synthesizes project execution health, milestone slippage, unresolved risk exposure, and partner engagement into actionable next steps.
- **Deterministic Fallback Engine**: Analyzes actual milestones, due dates, risk scores, and deliverable approvals. Works 100% offline without external AI keys.
- **Advisory Only**: Does not autonomously mutate project states, close risks, or approve milestones.
- **Endpoint**: `GET /api/v1/ai/projects/{project_id}/intelligence`.

### 5. Phase 3.10 — Security, Optimization & Production Hardening
- **Authentication & Privilege Protection**: Bcrypt password hashing, JWT bearer token expiration, inactive account blocking, and strict prevention of privileged role (`PLATFORM_ADMIN`, `GOVERNMENT_ADMIN`, `DISTRICT_NODAL_OFFICER`) self-assignment during registration.
- **Data Protection**: Password hashes and secret tokens are strictly excluded from all API response models (`UserResponse`).
- **Health & Probes**:
  - `GET /`: Welcome index
  - `GET /health`: Standard root health check
  - `GET /api/v1/health`: API prefix health check
  - `GET /api/v1/system/status`: Comprehensive system status with database connectivity and AI availability reporting (without secret leakage).
- **Persistence**: Supported on both PostgreSQL and local SQLite (`sqlite:///./jansetu.db`) with automatic table creation on startup.

### 6. Phase 3.6 – 3.11 API Endpoints Summary

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/api/v1/projects/{project_id}/impact` | `POST`, `GET` | Create and retrieve project impact assessments |
| `/api/v1/challenges/{challenge_id}/impact` | `GET` | Retrieve impact dossier for frontend Screen 09 |
| `/api/v1/challenges/{challenge_id}/impact/evidence` | `POST` | Submit field evidence values from Screen 09 |
| `/api/v1/impact/{impact_id}` | `GET`, `PATCH` | Inspect and update impact record details |
| `/api/v1/impact/{impact_id}/verify` | `POST` | Official government impact certification and signatory note |
| `/api/v1/impact/{impact_id}/reject` | `POST` | Government rejection of impact claim with feedback |
| `/api/v1/impact/{impact_id}/request-clarification`| `POST` | Request additional ground evidence |
| `/api/v1/impact/{impact_id}/evidence` | `POST`, `GET` | Attach and list field evidence artifacts |
| `/api/v1/evidence/{evidence_id}/verify` | `POST` | Government evaluation of individual evidence artifact |
| `/api/v1/analytics/overview` | `GET` | Platform-wide aggregation dashboard |
| `/api/v1/analytics/challenges` | `GET` | Challenges breakdown by district, domain, status |
| `/api/v1/analytics/projects` | `GET` | Projects execution and milestone progress analytics |
| `/api/v1/analytics/impact` | `GET` | Verified societal impact and village coverage metrics |
| `/api/v1/analytics/districts` | `GET` | District-level innovation metrics |
| `/api/v1/analytics/domains` | `GET` | Domain-level sectoral breakdown |
| `/api/v1/ai/projects/{project_id}/intelligence` | `GET` | Actionable project execution intelligence & risk warnings |

---

## Phase Scope Verification
- **Implemented**: All Phases from Phase 1.1 through Phase 3.11 are fully completed, integrated, and presentation-ready.
- **Design Philosophy**: AI remains strictly advisory; human government reviewers retain final authority; zero mock data; deterministic fallback guarantees 100% functionality without paid APIs.

