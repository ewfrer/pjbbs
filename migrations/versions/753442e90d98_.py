"""empty message

Revision ID: 753442e90d98
Revises: fac41427a30b
Create Date: 2018-09-29 16:45:16.818893

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '753442e90d98'
down_revision = 'fac41427a30b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('boarder', 'jijji')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('boarder', sa.Column('jijji', mysql.VARCHAR(length=20), nullable=True))
    # ### end Alembic commands ###