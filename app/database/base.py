from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all Digi-CoC database models.

    Every SQLAlchemy model will inherit from this class.
    Alembic will use this Base to detect database tables.
    """

    pass