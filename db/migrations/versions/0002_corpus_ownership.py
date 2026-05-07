"""add corpus_ownership table

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-07 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "corpus_ownership",
        sa.Column("corpus_id", sa.Text(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("corpus_id"),
    )
    op.create_index("ix_corpus_ownership_user_id", "corpus_ownership", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_corpus_ownership_user_id", table_name="corpus_ownership")
    op.drop_table("corpus_ownership")
