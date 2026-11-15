
"""Create organizations table."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = "f3ade69abbcd"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the organizations table."""

    op.create_table(
        "organizations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column(
            "organization_code",
            sa.String(length=50),
            nullable=False,
            unique=True,
        ),
        sa.Column("address", sa.String(length=300), nullable=True),
        sa.Column("contact_email", sa.String(length=150), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    """Remove the organizations table."""

    op.drop_table("organizations")
