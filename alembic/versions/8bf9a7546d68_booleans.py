"""booleans

Revision ID: 8bf9a7546d68
Revises: 15f7ea30022f
Create Date: 2026-06-02 16:39:07.566131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bf9a7546d68'
down_revision: Union[str, Sequence[str], None] = '15f7ea30022f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("performance_reviews", "level_change", type_ =sa.Boolean(), postgresql_using='level_change::boolean')
    op.alter_column("performance_reviews", "title_change", server_default=None)
    op.alter_column("performance_reviews", "title_change", type_ =sa.Boolean(), postgresql_using='title_change::boolean', server_default='FALSE')
    op.drop_constraint(
        "pr_draft_title_change_fkey",
        "pr_draft",
        type_="foreignkey",
    )
    op.alter_column("pr_draft", "level_change", type_ =sa.Boolean(), postgresql_using='level_change::boolean')
    op.alter_column("pr_draft", "title_change", type_ =sa.Boolean(), postgresql_using='title_change::boolean', server_default='FALSE')


def downgrade() -> None:
    """Downgrade schema."""
    pass
