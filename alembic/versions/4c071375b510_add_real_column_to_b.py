"""Add "real" column to build

Revision ID: 4c071375b510
Revises: 6d8008117a5
Create Date: 2014-08-04 14:44:47.207171

"""

# revision identifiers, used by Alembic.
revision = '4c071375b510'
down_revision = '6d8008117a5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('build', sa.Column('real', sa.Boolean(), server_default='false', nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('build', 'real')
    ### end Alembic commands ###
