"""empty message

Revision ID: 715cbd400615
Revises: de20f437c5f8
Create Date: 2018-10-07 14:43:26.275263

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '715cbd400615'
down_revision = 'de20f437c5f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['common_post.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tag')
    # ### end Alembic commands ###
