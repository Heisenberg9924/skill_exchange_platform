"""Add AI metadata, skill tags, and chat support."""

from alembic import op
import sqlalchemy as sa


revision = "20260414_0002"
down_revision = "20260401_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("skills", sa.Column("ai_summary", sa.Text(), nullable=True))
    op.add_column("skills", sa.Column("search_document", sa.Text(), nullable=True))

    op.create_table(
        "skill_tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_skill_tags_id", "skill_tags", ["id"], unique=False)
    op.create_index("ix_skill_tags_name", "skill_tags", ["name"], unique=False)

    op.create_table(
        "chat_threads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange_request_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["exchange_request_id"], ["exchange_requests.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("exchange_request_id"),
    )
    op.create_index("ix_chat_threads_id", "chat_threads", ["id"], unique=False)

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("thread_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["thread_id"], ["chat_threads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_chat_messages_id", "chat_messages", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_chat_messages_id", table_name="chat_messages")
    op.drop_table("chat_messages")

    op.drop_index("ix_chat_threads_id", table_name="chat_threads")
    op.drop_table("chat_threads")

    op.drop_index("ix_skill_tags_name", table_name="skill_tags")
    op.drop_index("ix_skill_tags_id", table_name="skill_tags")
    op.drop_table("skill_tags")

    op.drop_column("skills", "search_document")
    op.drop_column("skills", "ai_summary")
