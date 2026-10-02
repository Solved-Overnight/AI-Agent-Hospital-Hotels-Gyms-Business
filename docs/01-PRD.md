# Dentist AI Agent --- Product Requirements Document (PRD)

**Version:** 1.0\
**Status:** Pre-Stage 5 baseline\
**Product:** Dentist AI Agent\
**Primary repository:** `Dentist-AI-Agent/backend`

## 1. Product Overview

Dentist AI Agent is an AI-powered conversational assistant for a dental
clinic website. Its purpose is to answer clinic questions, retrieve
trusted clinic-specific information, answer general/current questions
when appropriate, and support appointment workflows.

The system combines: - An LLM-powered conversational agent -
Clinic-specific RAG - Web search for current/general information -
MySQL-backed appointment management - Tool-based business actions -
Persistent conversation/memory capabilities - A future website/API
interface

The project is being developed incrementally so that each capability can
be independently tested before being connected to the full agent.

## 2. Problem Statement

Dental websites commonly require patients to find information about
clinic services, doctors, opening hours, policies, and appointments. A
conventional FAQ or contact form cannot reliably handle natural-language
conversations or perform transactional appointment operations.

The product should provide a single conversational interface that
can: 1. Understand patient questions. 2. Retrieve trusted clinic
information. 3. Use web search when information is current or outside
the clinic knowledge base. 4. Check appointment capacity. 5. Create
appointments safely. 6. Eventually support cancellation, rescheduling,
and patient lookup.

## 3. Goals

### Primary Goals

-   Provide accurate conversational answers.
-   Prefer clinic knowledge for clinic-specific facts.
-   Use web search for appropriate current/general information.
-   Maintain a reliable appointment source of truth in MySQL.
-   Prevent overbooking.
-   Assign sequential patient numbers per doctor per date.
-   Validate booking inputs.
-   Keep AI reasoning separate from authoritative business logic.
-   Provide a clean foundation for a production website integration.

### Non-Goals for the Current Version

-   Fixed procedure/service durations.
-   Fixed time-slot scheduling.
-   Autonomous diagnosis or treatment decisions.
-   Replacing a dentist or clinical professional.
-   Autonomous emergency medical decision-making.
-   Fully autonomous irreversible actions outside explicitly defined
    tools.

## 4. Users

### Patient / Website Visitor

Can: - Ask clinic questions. - Ask general dental-information
questions. - Ask about doctors. - Check appointment availability. -
Request an appointment. - Eventually cancel/reschedule an appointment.

### Clinic Staff

Can eventually: - Configure doctors. - Configure daily patient
capacity. - Review appointments. - Manage appointment status. - Maintain
clinic knowledge documents.

### System Administrator

Can: - Configure infrastructure and credentials. - Manage access. -
Monitor system health. - Maintain deployments and backups.

## 5. Core User Stories

### Information

-   As a patient, I want to ask questions naturally so I do not need to
    search through multiple pages.
-   As a patient, I want clinic-specific answers to come from trusted
    clinic information.
-   As a patient, I want current/general information to be retrieved
    from the web when appropriate.

### Appointment

-   As a patient, I want to know whether a doctor has remaining capacity
    on a particular date.
-   As a patient, I want to book an appointment without worrying about
    duplicate patient numbers.
-   As a patient, I want to receive my appointment ID and patient number
    after successful booking.
-   As clinic staff, I want daily capacity to be configurable per doctor
    and date.
-   As clinic staff, I want cancelled appointments not to consume active
    capacity.

## 6. Appointment Model

The current scheduling model is **daily capacity based**, not fixed
time-slot based.

Example:

``` text
Doctor: Dr. Sarah Ahmed
Date: 2026-09-16
Maximum patients: 20

Patient #1
Patient #2
...
Patient #20
```

Patient number is scoped to:

``` text
doctor + appointment date
```

The database enforces uniqueness for that combination.

The system does not currently use service duration or a fixed 30-minute
appointment duration.

## 7. Functional Requirements

### FR-01 --- Conversational Agent

The agent shall understand natural-language patient requests and select
appropriate tools.

### FR-02 --- Clinic Knowledge Retrieval

The agent shall retrieve clinic-specific information from the clinic
knowledge base.

### FR-03 --- Web Search

The agent may use web search for current or general information where
appropriate.

### FR-04 --- Doctor Data

The system shall maintain doctors with name, specialization, and active
status.

### FR-05 --- Daily Capacity

The system shall maintain maximum patient capacity per doctor per date.

### FR-06 --- Availability

The system shall determine availability using:

``` text
remaining capacity =
maximum daily capacity - scheduled appointments
```

### FR-07 --- Patient Number

The system shall assign the next patient number for a doctor/date.

### FR-08 --- Safe Booking

Booking shall execute inside a transaction and lock the relevant
daily-capacity record before capacity is checked and the patient number
is assigned.

### FR-09 --- Validation

The system shall validate doctor ID, patient name, phone, optional
email, and appointment date before booking.

### FR-10 --- Appointment Status

Appointments shall support status values such as `scheduled` and
`cancelled`.

### FR-11 --- Future Appointment Management

The system shall eventually support cancellation, rescheduling, and
patient lookup.

## 8. Non-Functional Requirements

### Reliability

-   Booking must not exceed configured daily capacity.
-   Database constraints must protect patient-number uniqueness.
-   Failed transactions must not create partial bookings.

### Security

-   Database credentials must not be hard-coded.
-   Secrets must be loaded from environment/configuration.
-   Patient information must not be unnecessarily exposed in logs.
-   Access to administrative operations must be restricted.

### Maintainability

-   Business logic should remain outside the LLM prompt.
-   Database operations should be implemented as deterministic
    tools/services.
-   Components should have clear responsibilities.

### Observability

The system should eventually record: - Tool execution success/failure -
Application errors - Booking events - Database errors - Request
identifiers

Logs should avoid unnecessary patient PII.

## 9. Success Criteria

The Stage 4 appointment backend is considered functional when: - A
doctor can have a configured daily capacity. - Availability correctly
reports remaining capacity. - Booking assigns patient numbers
sequentially. - Concurrent booking attempts cannot exceed capacity. -
Duplicate patient numbers are prevented by the database. - Invalid
booking input is rejected. - The agent can call the appointment tools
without manually calculating business rules.

## 10. Future Scope

-   Cancellation
-   Rescheduling
-   Patient lookup
-   Appointment confirmation workflows
-   Website/API endpoint
-   Authentication/authorization
-   Admin dashboard
-   Production observability
-   Automated testing/CI
-   Deployment
-   Backup/recovery
-   Human handoff
