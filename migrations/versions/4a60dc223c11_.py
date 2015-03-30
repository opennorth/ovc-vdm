"""empty message

Revision ID: 4a60dc223c11
Revises: 2732661b799a
Create Date: 2015-03-29 22:02:51.411483

"""

# revision identifiers, used by Alembic.
revision = '4a60dc223c11'
down_revision = '2732661b799a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('daily_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=True),
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
