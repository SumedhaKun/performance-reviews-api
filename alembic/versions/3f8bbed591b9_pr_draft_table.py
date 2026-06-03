"""pr draft table

Revision ID: 3f8bbed591b9
Revises: de27e5994f17
Create Date: 2026-06-02 00:48:32.081261

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3f8bbed591b9"
down_revision: Union[str, Sequence[str], None] = "de27e5994f17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "pr_draft",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=True
        ),
        sa.Column("review_period_start", sa.Date(), nullable=True),
        sa.Column("review_period_end", sa.Date(), nullable=True),
        sa.Column("review_date", sa.Date(), nullable=True),
        sa.Column(
            "reviewer_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=True
        ),
        sa.Column("overall_rating", sa.Integer(), nullable=True),
        sa.Column("category_1", sa.Integer(), nullable=True),
        sa.Column("category_2", sa.Integer(), nullable=True),
        sa.Column("category_3", sa.Integer(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "title_change", sa.Integer(), sa.ForeignKey("titles.id"), nullable=True
        ),
        sa.Column("level_change", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("pr_draft")
