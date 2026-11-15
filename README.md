# Digi-CoC Frontend

This repository folder contains the Digi-CoC user interface only.

## Current state

- Frontend: HTML, CSS and vanilla JavaScript.
- Old Node.js / Express / SQLite backend: removed from this frontend handover.
- Demo/sample records: removed from frontend JavaScript datasets and report case options.
- API integration: not yet implemented. The frontend is ready for the backend developer to connect once the FastAPI backend's routes and response schemas are agreed.

## Run locally

Open the project folder in VS Code and use the Live Server extension on `index.html`, or run a local static server from this directory:

```bash
python -m http.server 5500
```

Then open `http://localhost:5500`.

## Integration notes

See `INTEGRATION_NOTES.md` for the page inventory and connection handover notes.

## Important

Until API integration is complete, data-entry interactions are frontend-only and are not persisted. Do not use this UI as a live evidence-management system or for real case data yet.
