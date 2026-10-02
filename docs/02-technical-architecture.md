# Dentist AI Agent --- Technical Architecture Document

**Version:** 1.0\
**Status:** Architecture baseline\
**Primary stack:** Python, LangChain, SQLAlchemy, MySQL/MariaDB, Chroma,
Hugging Face embeddings, Groq

## 1. Architecture Principles

1.  The LLM decides which capability/tool is appropriate; it does not
    own business truth.
2.  The database is the source of truth for appointments.
3.  Clinic-specific information should come from the clinic knowledge
    base.
4.  Web search should be used when current/general information is
    required.
5.  Transactional operations must be deterministic and validated.
6.  Database constraints must enforce critical invariants.
7.  Components should remain independently testable.
8.  Patient data should be minimized in logs and model context.

## 2. High-Level Architecture

``` text
                        ┌─────────────────────┐
                        │   Dental Website    │
                        │   / Future Frontend │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │   API / App Layer   │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │   AI Agent Layer    │
                        │ LangChain + Groq    │
                        └──────┬──────┬───────┘
                               │      │
                ┌──────────────┘      └──────────────┐
                ▼                                     ▼
       ┌─────────────────┐                   ┌─────────────────┐
       │ Clinic RAG      │                   │ Web Search      │
       │ Chroma + HF     │                   │ Current/Public  │
       │ embeddings      │                   │ Information     │
       └────────┬────────┘                   └─────────────────┘
                │
                ▼
       ┌────────────────────────────────────────────────┐
       │              Business Tools                    │
       │ appointments.py / future service layer         │
       └────────────────────────┬───────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │ SQLAlchemy ORM      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ MySQL / MariaDB     │
                    │ Doctors             │
                    │ Daily Capacities    │
                    │ Appointments         │
                    └─────────────────────┘
```

## 3. Current Project Structure

``` text
Dentist-AI-Agent/
└── backend/
    ├── app/
    │   ├── agent/
    │   │   └── agent.py
    │   │
    │   ├── api/
    │   │
    │   ├── database/
    │   │   ├── __init__.py
    │   │   ├── database.py
    │   │   ├── models.py
    │   │   └── seed.py
    │   │
    │   ├── knowledge/
    │   │
    │   ├── memory/
    │   │
    │   ├── services/
    │   │
    │   ├── tools/
    │   │   ├── appointments.py
    │   │   ├── basic.py
    │   │   └── search.py
    │   │
    │   └── main.py
    │
    ├── tests/
    ├── src/
    ├── .env
    ├── pyproject.toml
    ├── README.md
    └── uv.lock
```

## 4. Data Model

### Doctor

``` text
id
name
specialization
active
```

Relationship:

``` text
Doctor 1 ─────── N Appointment
Doctor 1 ─────── N DailyCapacity
```

### DailyCapacity

``` text
id
doctor_id
appointment_date
maximum_patients
```

Constraint:

``` text
UNIQUE(doctor_id, appointment_date)
```

### Appointment

``` text
id
doctor_id
patient_number
patient_name
patient_phone
patient_email
appointment_date
status
created_at
```

Constraint:

``` text
UNIQUE(doctor_id, appointment_date, patient_number)
```

## 5. Appointment Transaction Flow

``` text
book_appointment()
       │
       ▼
Validate input
       │
       ▼
Verify active doctor
       │
       ▼
SELECT DailyCapacity
FOR UPDATE
       │
       ▼
Count scheduled appointments
       │
       ▼
Capacity available?
    ┌──┴──┐
   No    Yes
    │      │
    ▼      ▼
 Reject   MAX(patient_number)
             + 1
               │
               ▼
          INSERT appointment
               │
               ▼
             COMMIT
```

## 6. Concurrency Strategy

The relevant `DailyCapacity` row is locked using a database row-level
lock.

This prevents two concurrent booking transactions from both observing
the same remaining capacity and creating conflicting bookings.

The unique patient-number constraint provides a second database-level
safeguard.

## 7. RAG Architecture

Clinic documents are ingested into a vector database.

``` text
Clinic Documents
      ↓
Document Loading
      ↓
Chunking
      ↓
Hugging Face Embeddings
      ↓
Chroma Vector Store
      ↓
Retriever
      ↓
Agent Tool
      ↓
Patient Answer
```

Clinic-specific facts should not be invented by the LLM when the
relevant information is unavailable.

## 8. Agent Responsibilities

The agent is responsible for: - Understanding intent. - Selecting
tools. - Formulating patient-facing responses. - Asking for missing
information.

The agent is not responsible for: - Calculating final capacity. -
Generating authoritative patient numbers. - Directly writing SQL. -
Bypassing validation. - Claiming a booking without a successful database
transaction.

## 9. Deployment Direction

The target production flow is:

``` text
Browser
  ↓
Frontend
  ↓
HTTPS API
  ↓
Agent/Application
  ↓
Database + Vector Store + External Search/LLM
```

Secrets and database credentials must remain server-side.

## 10. Testing Strategy

### Unit Tests

-   Date validation
-   Phone validation
-   Capacity calculations
-   Patient-number generation
-   Doctor validation

### Integration Tests

-   MySQL booking
-   Transaction rollback
-   Capacity enforcement
-   Cancellation behavior
-   RAG retrieval

### Agent Tests

-   Tool selection
-   Missing-information handling
-   Booking confirmation behavior
-   Refusal to invent availability

### Concurrency Tests

Simulate simultaneous booking requests against the same doctor/date and
verify capacity is never exceeded.

## 11. Planned Evolution

The current architecture intentionally leaves room for:

``` text
services/
    appointment_service.py
    doctor_service.py

api/
    routes/
        appointments.py
        chat.py

memory/
    conversation_store.py

tests/
    unit/
    integration/
    agent/
```

The project should evolve toward service-layer separation before
becoming production-critical.
