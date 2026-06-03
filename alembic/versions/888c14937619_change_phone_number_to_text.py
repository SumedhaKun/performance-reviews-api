"""change phone number to text

Revision ID: 888c14937619
Revises: 3b6a22ea4853
Create Date: 2026-05-31 14:31:21.251595

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "888c14937619"
down_revision: Union[str, Sequence[str], None] = "3b6a22ea4853"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "employees", "phone", type_=sa.Text(), postgresql_using="phone::varchar"
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
