"""make level change and tital change booleans

Revision ID: 15f7ea30022f
Revises: 3f8bbed591b9
Create Date: 2026-06-02 15:28:21.029350

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "15f7ea30022f"
down_revision: Union[str, Sequence[str], None] = "3f8bbed591b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # op.alter_column("performance_reviews", "level_change", type_ =sa.Boolean(), postgresql_using='level_change::boolean')
    # op.alter_column("performance_reviews", "title_change", server_default=None)
    # op.alter_column("performance_reviews", "title_change", type_ =sa.Boolean(), postgresql_using='title_change::boolean', server_default='FALSE')
    # op.drop_constraint(
    #    "pr_draft_title_change_fkey",
    #    "pr_draft",
    #    type_="foreignkey",
    # )
    # op.alter_column("pr_draft", "level_change", type_ =sa.Boolean(), postgresql_using='level_change::boolean')
    # op.alter_column("pr_draft", "title_change", type_ =sa.Boolean(), postgresql_using='title_change::boolean', server_default='FALSE')

    op.create_index(
        "appraisals_employee_id_index",
        "appraisals",
        ["employee_id"],
    )
    op.create_index(
        "comments_commenter_id_index",
        "comments",
        ["commenter_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
