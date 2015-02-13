"""empty message

Revision ID: 4dd568a56e6b
Revises: 3b43ee44d982
Create Date: 2015-01-21 20:58:51.340565

"""

# revision identifiers, used by Alembic.
revision = '4dd568a56e6b'
down_revision = '3b43ee44d982'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('releases', sa.Column('decription', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('releases', 'decription')
    ### end Alembic commands ###