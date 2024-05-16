"""Changed image_path to String

Revision ID: c8d62a095c9b
Revises: bcea5c72cd01
Create Date: 2024-05-16 09:51:10.404700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8d62a095c9b'
down_revision = 'bcea5c72cd01'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('offer', schema=None) as batch_op:
        batch_op.alter_column('image_path',
               existing_type=sa.BLOB(),
               type_=sa.String(),
               existing_nullable=False)
        batch_op.drop_column('price')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('offer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price', sa.FLOAT(), nullable=False))
        batch_op.alter_column('image_path',
               existing_type=sa.String(),
               type_=sa.BLOB(),
               existing_nullable=False)

    # ### end Alembic commands ###