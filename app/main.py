
from fastapi import FastAPI

from app.database.connections import test_database_connection
from app.routers.organizations import router as organizations_router

app = FastAPI(
    title="Digi-CoC Backend",
    description="Digital Chain of Custody Backend API",
    version="1.0.0",
)

test_database_connection()

app.include_router(organizations_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Digi-CoC Backend",
    }
