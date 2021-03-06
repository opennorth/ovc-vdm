"""empty message

Revision ID: 563b0308900f
Revises: 38acd2fec579
Create Date: 2015-03-29 17:15:15.725965

"""

# revision identifiers, used by Alembic.
revision = '563b0308900f'
down_revision = '38acd2fec579'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('daily_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('datetime', sa.String(), nullable=True),
    sa.Column('path', sa.String(), nullable=True),
    sa.Column('args', postgresql.JSON(), nullable=True),
    sa.Column('referrer', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('daily_stats')
    ### end Alembic commands ###
