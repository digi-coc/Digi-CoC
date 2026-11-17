
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Load the database URL from the existing application settings.
DATABASE_URL = settings.database_url


# Create the database engine.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# Create the database session factory.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# Provide database sessions to FastAPI endpoints.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
