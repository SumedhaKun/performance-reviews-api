"""add indexes

Revision ID: de27e5994f17
Revises: 888c14937619
Create Date: 2026-06-01 21:22:30.547341

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "de27e5994f17"
down_revision: Union[str, Sequence[str], None] = "888c14937619"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op


def upgrade() -> None:
    """Upgrade schema."""

    op.create_index(
        "comment_employee_index",
        "comments",
        ["employee_id"],
    )

    op.create_index(
        "company_department_index",
        "employees",
        ["company_id", "department"],
    )

    op.create_index(
        "stats_employee_id_index",
        "performance_reviews",
        ["employee_id"],
    )


def downgrade() -> None:
    op.drop_index("stats_employee_id_index", table_name="performance_reviews")
    op.drop_index("company_department_index", table_name="employees")
    op.drop_index("comment_employee_index", table_name="comments")
