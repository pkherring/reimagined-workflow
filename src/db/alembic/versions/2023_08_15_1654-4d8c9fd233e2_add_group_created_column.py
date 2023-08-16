"""add group created column

Revision ID: 4d8c9fd233e2
Revises: fe137ebd03cc
Create Date: 2023-08-15 16:54:25.141782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d8c9fd233e2'
down_revision: Union[str, None] = 'fe137ebd03cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("groups", sa.Column("date_created", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column("groups", "date_created")
    # ### end Alembic commands ###
