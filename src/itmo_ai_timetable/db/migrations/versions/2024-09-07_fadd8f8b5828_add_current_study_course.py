"""add_current_study_course

Revision ID: fadd8f8b5828
Revises: c025cf043a37
Create Date: 2024-09-07 21:45:09.728077

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fadd8f8b5828"
down_revision: str | None = "c025cf043a37"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("studying_course", sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "studying_course")
    # ### end Alembic commands ###
