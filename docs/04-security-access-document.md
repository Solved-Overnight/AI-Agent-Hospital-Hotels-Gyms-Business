# Dentist AI Agent --- Security & Access Document

**Version:** 1.0\
**Purpose:** Define who can access which parts of the system and how
access should be controlled.

## 1. Access Control Principles

The application should follow:

-   Least privilege
-   Default deny
-   Need-to-know access
-   Separation of patient and administrative capabilities
-   Server-side authorization
-   No trust based solely on frontend controls

## 2. Roles

### Patient

Can: - Use the conversational assistant. - Ask public clinic
questions. - Check appointment availability. - Create their own
appointment. - Eventually cancel/reschedule according to clinic policy.

Cannot: - Configure doctors. - Configure capacity. - View other
patients. - Access database credentials. - Access internal logs.

### Clinic Staff

Can: - View appointments required for clinic operations. - Update
appointment status. - Manage approved doctor information. - Configure
daily capacity if authorized.

Cannot: - Access application secrets through the website. - Access
infrastructure unless separately authorized.

### Clinic Administrator

Can: - Manage staff access. - Manage doctors. - Manage capacity. -
Review operational logs. - Manage clinic knowledge documents. - Perform
approved administrative operations.

### System Administrator / Developer

Can: - Deploy and maintain infrastructure. - Manage application
configuration. - Manage database infrastructure. - Rotate credentials. -
Access technical logs according to organizational policy.

Production access should be controlled and audited.

## 3. Access Matrix

  Resource / Action                Patient        Staff        Admin   System Admin
  --------------------------- ------------ ------------ ------------ --------------
  Public clinic information           Read         Read   Read/Write      Technical
  Web information                      Use          Use          Use      Technical
  Check availability                   Yes          Yes          Yes            Yes
  Create appointment                   Yes          Yes          Yes            Yes
  View own appointment               Yes\*          Yes          Yes            Yes
  View all appointments                 No          Yes          Yes            Yes
  Cancel appointment            Own/Policy          Yes          Yes            Yes
  Reschedule appointment        Own/Policy          Yes          Yes            Yes
  Manage doctors                        No   Authorized          Yes            Yes
  Manage daily capacity                 No   Authorized          Yes            Yes
  Manage clinic documents               No   Authorized          Yes            Yes
  Application configuration             No           No      Limited            Yes
  Database administration               No           No           No            Yes

`*` Patient self-service access should require an appropriate
verification mechanism.

## 4. Authentication

Production administrative interfaces should require authentication.

Possible authentication methods: - Secure session authentication -
OAuth/OIDC - Organization-managed identity provider

Passwords, if used, must never be stored in plaintext.

## 5. Authorization

Authentication answers:

> Who are you?

Authorization answers:

> What are you allowed to do?

Every protected API operation should enforce authorization server-side.

Example:

``` text
POST /appointments
    → authenticated/authorized operation

POST /admin/capacity
    → staff/admin permission required

GET /admin/appointments
    → staff/admin permission required
```

A frontend button being hidden is not an authorization mechanism.

## 6. Patient Data Access

Patients must not be able to enumerate or retrieve other patients'
records.

Do not expose predictable database IDs as the sole authorization
mechanism.

For patient self-service, use an approved verification flow such as: -
Secure login - One-time verification code - Appointment-specific secure
token

The exact mechanism should be selected before production launch.

## 7. Database Access

The application should connect using a dedicated database user.

Example conceptual separation:

``` text
Application
   ↓
dentist_ai application user
   ↓
dentist_ai database
```

The root database account should not be used by the application.

Administrative database access should be restricted to authorized
operators.

## 8. API Access

The API should eventually implement: - Authentication - Authorization -
Request validation - Rate limiting - Secure headers - CORS
restrictions - Audit logging for administrative actions

## 9. Rate Limiting

Rate limiting should be applied to: - Chat endpoints - Appointment
creation - Authentication - Verification-code requests - Administrative
APIs

This reduces abuse and protects external LLM/search costs.

## 10. Audit Events

The system should record security-relevant administrative events such
as:

``` text
staff_login
admin_login
doctor_created
doctor_updated
capacity_created
capacity_updated
appointment_cancelled_by_staff
appointment_rescheduled_by_staff
knowledge_document_updated
permission_changed
```

Audit records should not unnecessarily store patient conversation
contents.

## 11. Credential Rotation

The system should support rotation of: - Database passwords - LLM API
keys - Search/API credentials - Authentication secrets

Keys should be rotated immediately if exposure is suspected.

## 12. Production Access Review

Access should be reviewed periodically.

When a staff member leaves or changes responsibilities: 1. Disable or
modify access. 2. Revoke active sessions where appropriate. 3. Review
assigned permissions. 4. Rotate shared credentials if any were used.

Shared administrator accounts should be avoided.

## 13. Access-Control Checklist

-   [ ] Authentication implemented
-   [ ] Role model implemented
-   [ ] Server-side authorization implemented
-   [ ] Patient isolation verified
-   [ ] Admin routes protected
-   [ ] Database root account not used by app
-   [ ] Least-privilege DB permissions
-   [ ] Rate limiting enabled
-   [ ] Audit logging enabled
-   [ ] Credential rotation process documented
-   [ ] Staff offboarding process documented
-   [ ] Access review process documented
