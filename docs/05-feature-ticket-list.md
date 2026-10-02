# Dentist AI Agent --- Feature Ticket List

**Version:** 1.0\
**Purpose:** Development backlog and implementation sequence

## Ticket Status Legend

-   `DONE` --- implemented and verified
-   `IN PROGRESS` --- currently being implemented
-   `NEXT` --- immediate next development item
-   `PLANNED` --- future implementation
-   `BLOCKED` --- depends on another item

------------------------------------------------------------------------

# Epic 1 --- Foundation

## DAI-001 --- Project Structure

**Status:** DONE

Maintain the modular backend structure:

``` text
app/
├── agent/
├── api/
├── database/
├── knowledge/
├── memory/
├── services/
├── tools/
└── main.py
```

## DAI-002 --- Environment Configuration

**Status:** DONE

Load database and external API configuration from environment variables.

## DAI-003 --- Database Connection

**Status:** DONE

Implement SQLAlchemy engine, session factory, and declarative base.

------------------------------------------------------------------------

# Epic 2 --- AI Agent

## DAI-010 --- Modern LangChain Agent

**Status:** DONE

Implement the current LangChain agent architecture with tool calling.

## DAI-011 --- Groq LLM Integration

**Status:** DONE

Use Groq as the current LLM provider.

## DAI-012 --- Basic Clinic Tools

**Status:** DONE

Implement basic deterministic tools used by the agent.

## DAI-013 --- Web Search Tool

**Status:** DONE

Implement web search for current/general information.

------------------------------------------------------------------------

# Epic 3 --- Clinic Knowledge / RAG

## DAI-020 --- Clinic Document Ingestion

**Status:** DONE

Load clinic documents into the knowledge pipeline.

## DAI-021 --- Embedding Generation

**Status:** DONE

Generate embeddings using the selected Hugging Face embedding model.

## DAI-022 --- Chroma Vector Store

**Status:** DONE

Store clinic document vectors in Chroma.

## DAI-023 --- Clinic Retriever

**Status:** DONE

Implement retrieval of clinic-specific information.

## DAI-024 --- RAG Agent Integration

**Status:** PLANNED

Connect retrieval to the agent with explicit source/authority rules.

------------------------------------------------------------------------

# Epic 4 --- Appointment System

## DAI-030 --- Doctor Model

**Status:** DONE

Create doctor database model with: - ID - Name - Specialization - Active
status

## DAI-031 --- Daily Capacity Model

**Status:** DONE

Create per-doctor/per-date daily capacity.

Constraint:

``` text
UNIQUE(doctor_id, appointment_date)
```

## DAI-032 --- Patient Number

**Status:** DONE

Add sequential patient number per doctor/date.

Constraint:

``` text
UNIQUE(doctor_id, appointment_date, patient_number)
```

## DAI-033 --- Capacity Availability

**Status:** DONE

Implement availability based on:

``` text
maximum_patients - scheduled_appointments
```

## DAI-034 --- Transaction-Safe Booking

**Status:** DONE

Lock the relevant daily-capacity row before: - Counting active
bookings - Calculating the next patient number - Creating the
appointment

## DAI-035 --- Booking Validation

**Status:** DONE

Validate: - Doctor ID - Doctor active status - Patient name - Patient
phone - Patient email - Appointment date - Daily capacity

## DAI-036 --- Remove Fixed Duration Scheduling

**Status:** IN PROGRESS

Remove obsolete fixed 30-minute appointment logic and unused start/end
time fields so the schema matches the capacity-based queue model.

## DAI-037 --- Appointment Tests

**Status:** NEXT

Add automated tests for: - First patient number - Sequential numbering -
Full capacity - Cancelled appointments - Invalid input - Unknown
doctor - Missing capacity - Concurrent booking

------------------------------------------------------------------------

# Epic 5 --- Appointment Lifecycle

## DAI-040 --- Appointment Lookup

**Status:** PLANNED

Allow authorized users to find an appointment using an approved
verification method.

## DAI-041 --- Cancellation

**Status:** PLANNED

Allow patients/staff to cancel appointments according to policy.

Cancellation should change status rather than delete the historical
record.

## DAI-042 --- Rescheduling

**Status:** PLANNED

Allow an appointment to move to another eligible date.

The operation must: - Validate destination capacity. - Preserve data
integrity. - Avoid duplicate patient numbers. - Use a transaction.

## DAI-043 --- Appointment Status Model

**Status:** PLANNED

Define allowed states, for example:

``` text
scheduled
cancelled
completed
no_show
```

Transitions should be controlled by business rules.

------------------------------------------------------------------------

# Epic 6 --- Application Services

## DAI-050 --- Appointment Service Layer

**Status:** PLANNED

Move complex appointment business logic from LangChain tools into a
dedicated service layer.

Target:

``` text
tools/
    appointments.py

services/
    appointment_service.py
```

Tools should become thin adapters around deterministic services.

## DAI-051 --- Doctor Service

**Status:** PLANNED

Centralize doctor-related business operations.

## DAI-052 --- Capacity Service

**Status:** PLANNED

Centralize daily capacity management.

------------------------------------------------------------------------

# Epic 7 --- API

## DAI-060 --- Chat API

**Status:** PLANNED

Expose the agent through a secure HTTP API.

## DAI-061 --- Appointment API

**Status:** PLANNED

Expose controlled appointment operations.

## DAI-062 --- Admin API

**Status:** PLANNED

Provide protected endpoints for staff/admin operations.

## DAI-063 --- API Validation

**Status:** PLANNED

Add request/response schemas and validation.

------------------------------------------------------------------------

# Epic 8 --- Memory

## DAI-070 --- Conversation Persistence

**Status:** PLANNED

Persist conversation state using the project's memory architecture.

## DAI-071 --- Patient Context Controls

**Status:** PLANNED

Define what patient information can be retained and for how long.

## DAI-072 --- Memory Privacy

**Status:** PLANNED

Ensure sensitive information is not unnecessarily retained or exposed to
unrelated sessions.

------------------------------------------------------------------------

# Epic 9 --- Security

## DAI-080 --- Authentication

**Status:** PLANNED

Implement authentication for protected APIs.

## DAI-081 --- Role-Based Authorization

**Status:** PLANNED

Implement patient/staff/admin access controls.

## DAI-082 --- Rate Limiting

**Status:** PLANNED

Protect chat, booking, authentication, and admin endpoints.

## DAI-083 --- Secure Logging

**Status:** PLANNED

Minimize patient PII in logs.

## DAI-084 --- Audit Logging

**Status:** PLANNED

Record security-sensitive administrative actions.

## DAI-085 --- Secret Management

**Status:** PLANNED

Move production secrets into a secure secret-management mechanism.

------------------------------------------------------------------------

# Epic 10 --- Testing & Quality

## DAI-090 --- Unit Test Suite

**Status:** PLANNED

Test deterministic business logic independently.

## DAI-091 --- Database Integration Tests

**Status:** PLANNED

Test real database behavior.

## DAI-092 --- Agent Tool Tests

**Status:** PLANNED

Verify tool selection and tool outputs.

## DAI-093 --- Prompt Injection Tests

**Status:** PLANNED

Test malicious instructions in: - Patient messages - Retrieved
documents - Web content

## DAI-094 --- Concurrency Tests

**Status:** PLANNED

Verify capacity cannot be exceeded under simultaneous booking attempts.

## DAI-095 --- End-to-End Tests

**Status:** PLANNED

Test:

``` text
Website
  → API
  → Agent
  → Tool
  → Database
  → Response
```

------------------------------------------------------------------------

# Epic 11 --- Production

## DAI-100 --- Production Configuration

**Status:** PLANNED

Separate development and production configuration.

## DAI-101 --- Database Backup

**Status:** PLANNED

Implement and test backup/restore.

## DAI-102 --- Monitoring

**Status:** PLANNED

Monitor: - API health - Error rate - Database health - LLM failures -
Tool failures - Booking failures

## DAI-103 --- Deployment

**Status:** PLANNED

Deploy backend and frontend using a controlled production process.

## DAI-104 --- Incident Response

**Status:** PLANNED

Document security and operational incident procedures.

------------------------------------------------------------------------

# Immediate Development Sequence

After Stage 4A, the recommended implementation order is:

``` text
DAI-037  Appointment Tests
    ↓
DAI-040  Appointment Lookup
    ↓
DAI-041  Cancellation
    ↓
DAI-042  Rescheduling
    ↓
DAI-043  Appointment Status
    ↓
DAI-050  Appointment Service Layer
    ↓
DAI-060  Chat API
    ↓
DAI-061  Appointment API
    ↓
DAI-070  Conversation Persistence
    ↓
DAI-080  Authentication
    ↓
DAI-081  Authorization
    ↓
DAI-090  Unit/Integration Tests
    ↓
DAI-100+ Production Readiness
```

## Definition of Done

A ticket is considered complete only when: 1. Code is implemented. 2.
The relevant database/schema change is complete. 3. Validation/error
behavior is defined. 4. Automated tests exist where applicable. 5. The
agent/tool behavior is verified if applicable. 6. Documentation is
updated. 7. No unrelated functionality is silently changed.
