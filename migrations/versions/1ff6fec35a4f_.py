"""empty message

Revision ID: 1ff6fec35a4f
Revises: 55c35f083596
Create Date: 2015-03-06 12:39:20.829269

"""

# revision identifiers, used by Alembic.
revision = '1ff6fec35a4f'
down_revision = '55c35f083596'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('releases', sa.Column('procuring_entity', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('releases', 'procuring_entity')
    ### end Alembic commands ###
