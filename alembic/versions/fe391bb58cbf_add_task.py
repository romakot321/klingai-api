"""add task

Revision ID: fe391bb58cbf
Revises: 
Create Date: 2025-05-14 18:20:52.567005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe391bb58cbf'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('external_id', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('app_id', sa.String(), nullable=False),
    sa.Column('prompt', sa.String(), nullable=True),
    sa.Column('webhook_url', sa.String(), nullable=True),
    sa.Column('result', sa.String(), nullable=True),
    sa.Column('error', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('tasks_pkey'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tasks')
    # ### end Alembic commands ###
