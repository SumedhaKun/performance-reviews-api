"""idempotency for pr submissions

Revision ID: da53500bf1db
Revises: 8bf9a7546d68
Create Date: 2026-06-02 23:23:17.965868

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "da53500bf1db"
down_revision: Union[str, Sequence[str], None] = "8bf9a7546d68"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "submitted_pr_drafts",
        sa.Column("draft_id", sa.Integer(), primary_key=True),
        sa.Column("review_id", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("submitted_pr_drafts")
