"""empty message

Revision ID: 33fa645dbb31
Revises: 1ff6fec35a4f
Create Date: 2015-03-22 15:59:07.549849

"""

# revision identifiers, used by Alembic.
revision = '33fa645dbb31'
down_revision = '1ff6fec35a4f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sources', sa.Column('type', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sources', 'type')
    ### end Alembic commands ###
