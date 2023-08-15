"""add user created column

Revision ID: dbb43029aa7a
Revises: 4d8c9fd233e2
Create Date: 2023-08-15 17:18:27.022954

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'dbb43029aa7a'
down_revision: Union[str, None] = '4d8c9fd233e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', 
                  sa.Column('date_created', sa.DateTime(timezone=True), nullable=True)
                  )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column('users', 'date_created')
    # ### end Alembic commands ###
