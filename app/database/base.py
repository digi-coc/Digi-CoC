from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Common SQLAlchemy base class for all Digi-CoC models.

    Every database model inherits from this class.
    Alembic uses Base.metadata to identify database tables
    when generating migrations.
    """

    pass
