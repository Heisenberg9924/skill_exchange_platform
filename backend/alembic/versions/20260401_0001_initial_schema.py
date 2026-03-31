"""Initial schema for skill exchange platform."""

from alembic import op
import sqlalchemy as sa


revision = "20260401_0001"
down_revision = None
branch_labels = None
depends_on = None


skill_type_enum = sa.Enum("OFFER", "REQUEST", name="skilltype")
exchange_status_enum = sa.Enum(
    "PENDING",
    "ACCEPTED",
    "REJECTED",
    "CANCELLED",
    "COMPLETED",
    name="exchangerequeststatus",
)


def upgrade() -> None:
    bind = op.get_bind()
    skill_type_enum.create(bind, checkfirst=True)
    exchange_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("profile_photo_url", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("skill_type", skill_type_enum, nullable=False),
        sa.Column("proficiency_level", sa.String(length=50), nullable=True),
        sa.Column("availability", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_skills_id", "skills", ["id"], unique=False)
    op.create_index("ix_skills_title", "skills", ["title"], unique=False)
    op.create_index("ix_skills_category", "skills", ["category"], unique=False)

    op.create_table(
        "exchange_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("requester_id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("requested_skill_id", sa.Integer(), nullable=False),
        sa.Column("offered_skill_id", sa.Integer(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", exchange_status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["requester_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipient_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["offered_skill_id"], ["skills.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_exchange_requests_id", "exchange_requests", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_exchange_requests_id", table_name="exchange_requests")
    op.drop_table("exchange_requests")

    op.drop_index("ix_skills_category", table_name="skills")
    op.drop_index("ix_skills_title", table_name="skills")
    op.drop_index("ix_skills_id", table_name="skills")
    op.drop_table("skills")

    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    exchange_status_enum.drop(bind, checkfirst=True)
    skill_type_enum.drop(bind, checkfirst=True)
