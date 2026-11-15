from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker


from app.core.config import settings


# Create the SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=True
)


def test_database_connection():
    """
    Tests the connection between the Digi-CoC backend
    and the PostgreSQL database.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))

            print("================================")
            print("PostgreSQL connection successful!")
            print("Database test result:", result.scalar())
            print("================================")

    except Exception as error:
        print("================================")
        print("PostgreSQL connection failed!")
        print("Error:", error)
        print("================================")


# Create a factory for database sessions.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db():
    """Provide a database session for one API request."""
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()
