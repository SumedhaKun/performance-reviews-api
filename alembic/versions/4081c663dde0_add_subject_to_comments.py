"""add subject to comments

Revision ID: 4081c663dde0
Revises: 2eee7e2708c9
Create Date: 2026-05-10 18:55:52.652579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4081c663dde0'
down_revision: Union[str, Sequence[str], None] = '2eee7e2708c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "comments",
        sa.Column("subject", sa.Text(), nullable=False, server_default=""),
    )
    op.alter_column("comments", "subject", server_default=None)


def downgrade() -> None:
    op.drop_column("comments", "subject")
