"""Add cached embedding vectors for semantic ranking."""

from alembic import op
import sqlalchemy as sa


revision = "20260414_0003"
down_revision = "20260414_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("skills", sa.Column("embedding_vector", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("skills", "embedding_vector")
