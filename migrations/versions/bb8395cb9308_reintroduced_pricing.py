"""Reintroduced pricing

Revision ID: bb8395cb9308
Revises: c8d62a095c9b
Create Date: 2024-05-16 10:47:21.654639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb8395cb9308'
down_revision = 'c8d62a095c9b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('offer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('min_price', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('max_price', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('offer', schema=None) as batch_op:
        batch_op.drop_column('max_price')
        batch_op.drop_column('min_price')

    # ### end Alembic commands ###
