# Digi-CoC Frontend — Backend Handover Notes

## What is included

The frontend is a static HTML/CSS/JavaScript application. The visual pages and existing UI interactions have been retained.

| Page | Main responsibility |
|---|---|
| `index.html` | Dashboard and summary |
| `case.html` | Case management |
| `evidence.html` | Evidence registration and listing |
| `custody.html` | Custody records and transfer workflow |
| `personnel.html` | System personnel and evidence-handler management |
| `devices.html` | Device management/status |
| `scan.html` | Evidence tag lookup workflow |
| `reports.html` | Report preview/printing |
| `audit.html` | Audit log view |

## What was removed

- The old `backend/` directory, including its Express server, SQLite database module, SQLite development database and database backup.
- Hardcoded demo records in dashboard, cases, evidence, custody, devices, scan registry, reports and audit JavaScript datasets.
- Hardcoded sample case choices from the report-case selector.

The original uploaded ZIP remains the user's backup of the previous project state.

## Current integration status

A source scan found no existing frontend `fetch()` calls or configured HTTP API base URL. The previous Express/SQLite backend was present as a separate folder, but the frontend pages were not calling it.

No FastAPI endpoint paths have been assumed or hardcoded in this handover. The frontend developer and backend developer should agree the actual OpenAPI routes, request/response schemas, authentication flow, pagination, error format and organisation scoping before implementing the API client.

## Suggested connection work for backend developer

1. Share the FastAPI OpenAPI document (`/openapi.json` or Swagger UI) and confirm the deployed API base URL.
2. Agree endpoint contracts for dashboard summaries, cases, evidence, custody transfers, personnel, devices, scan/tag lookup, reports and audit events.
3. Implement one shared frontend API client (base URL from environment/configuration, JSON handling, auth token handling, consistent errors).
4. Replace each page's empty data source with API loading and submission calls.
5. Add loading, empty, validation and API-error states to every page.
6. Ensure the frontend never receives or stores raw fingerprint templates. Biometric enrolment/verification should use the secured device/backend flow defined in the backend specification.
7. Test role/organisation isolation, expired sessions, duplicate identifiers, failed biometric verification, offline device states and audit event creation.

## Important operational warning

This is a frontend handover, not a live system. Until the API is connected and end-to-end tested, records entered into the interface are not persisted and must not be used for real forensic cases or evidence custody.
