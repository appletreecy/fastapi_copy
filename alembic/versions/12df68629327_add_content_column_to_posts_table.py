"""add content column to posts table

Revision ID: 12df68629327
Revises: bd1f3062bb5c
Create Date: 2024-06-15 14:35:03.951722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12df68629327'
down_revision: Union[str, None] = 'bd1f3062bb5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column("posts", 'content')
    pass
