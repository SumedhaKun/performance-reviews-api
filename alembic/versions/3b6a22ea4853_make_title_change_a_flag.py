"""make title_change a flag

Revision ID: 3b6a22ea4853
Revises: 7b4b63b4a9d1
Create Date: 2026-05-26 15:18:49.222445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b6a22ea4853'
down_revision: Union[str, Sequence[str], None] = '4081c663dde0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "performance_reviews_title_change_fkey",
        "performance_reviews",
        type_="foreignkey",
    )
    op.alter_column(
        "performance_reviews",
        "title_change",
        existing_type=sa.Integer(),
        server_default=sa.text("0"),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "performance_reviews",
        "title_change",
        existing_type=sa.Integer(),
        server_default=None,
        existing_nullable=False,
    )
    op.create_foreign_key(
        "performance_reviews_title_change_fkey",
        "performance_reviews",
        "titles",
        ["title_change"],
        ["id"],
    )