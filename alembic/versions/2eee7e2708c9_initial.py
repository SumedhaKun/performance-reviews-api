"""initial

Revision ID: 2eee7e2708c9
Revises:
Create Date: 2026-05-03 17:32:07.999523

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2eee7e2708c9"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("industry", sa.Text(), nullable=False),
        sa.Column("headquarters_location", sa.Text(), nullable=False),
        sa.Column("founded_date", sa.Date(), nullable=True),
        sa.Column(
            "active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
    )

    op.create_table(
        "titles",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
    )

    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False
        ),
        sa.Column("first_name", sa.Text(), nullable=False),
        sa.Column("last_name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("phone", sa.Integer(), nullable=False),
        sa.Column("title_id", sa.Integer(), sa.ForeignKey("titles.id"), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("department", sa.Text(), nullable=False),
        sa.Column("hire_date", sa.Date(), nullable=False),
        sa.Column(
            "current_employee",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False
        ),
        sa.Column(
            "commenter_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.TIMESTAMP, server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "appraisals",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False
        ),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.TIMESTAMP, server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "performance_reviews",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False
        ),
        sa.Column("review_period_start", sa.Date(), nullable=False),
        sa.Column("review_period_end", sa.Date(), nullable=False),
        sa.Column("review_date", sa.Date(), nullable=False),
        sa.Column(
            "reviewer_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False
        ),
        sa.Column("overall_rating", sa.Integer(), nullable=False),
        sa.Column("category_1", sa.Integer(), nullable=False),
        sa.Column("category_2", sa.Integer(), nullable=False),
        sa.Column("category_3", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column(
            "title_change", sa.Integer(), sa.ForeignKey("titles.id"), nullable=False
        ),
        sa.Column("level_change", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("performance_reviews")
    op.drop_table("appraisals")
    op.drop_table("comments")
    op.drop_table("employees")
    op.drop_table("titles")
    op.drop_table("companies")
