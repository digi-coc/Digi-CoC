
from fastapi import FastAPI

from app.routers.organizations import router as organizations_router
from app.routers.cases import router as cases_router
from app.routers.evidence import router as evidence_router
from app.routers.evidence_images import router as evidence_images_router
from app.routers.evidence_tags import router as evidence_tags_router
from app.routers.personnel import router as personnel_router
from app.routers.devices import router as devices_router
from app.routers.custody_events import router as custody_events_router

from app.routers.unauthorized_attempts import (
    router as unauthorized_attempts_router,
)

from app.routers.biometric_verifications import (
    router as biometric_verifications_router,
)

from app.routers.audit_logs import router as audit_logs_router
from app.routers.access_requests import router as access_requests_router

from app.routers.access_request_reviews import (
    router as access_request_reviews_router,
)

from app.routers.auth import router as auth_router

from app.routers.biometric_enrollments import (
    router as biometric_enrollments_router,
)

from app.routers.biometric_templates import (
    router as biometric_templates_router,
)


app = FastAPI(
    title="Digi-CoC Backend",
    description="Digital Chain of Custody Backend API",
    version="1.0.0",
)


# Register each API router exactly once.

app.include_router(organizations_router)
app.include_router(cases_router)
app.include_router(evidence_router)
app.include_router(evidence_images_router)
app.include_router(evidence_tags_router)
app.include_router(personnel_router)
app.include_router(devices_router)
app.include_router(custody_events_router)
app.include_router(unauthorized_attempts_router)
app.include_router(biometric_verifications_router)
app.include_router(audit_logs_router)
app.include_router(access_requests_router)
app.include_router(access_request_reviews_router)
app.include_router(auth_router)
app.include_router(biometric_enrollments_router)
app.include_router(biometric_templates_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "Digi-CoC Backend",
    }

