"""test

Revision ID: bcea5c72cd01
Revises: 
Create Date: 2024-05-16 08:59:41.961273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcea5c72cd01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('display_name', sa.String(length=64), nullable=False),
    sa.Column('hashed_password', sa.String(length=128), nullable=True),
    sa.Column('artist_title', sa.String(length=128), nullable=True),
    sa.Column('artist_description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)

    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_path', sa.String(length=100), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_from', sa.Integer(), nullable=True),
    sa.Column('user_to', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('text_content', sa.Text(), nullable=False),
    sa.Column('is_read', sa.Integer(), nullable=False),
    sa.CheckConstraint('user_from != user_to'),
    sa.ForeignKeyConstraint(['user_from'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_to'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('offer',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('form_path', sa.Text(), nullable=True),
    sa.Column('image_path', sa.BLOB(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('session',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('session_id', sa.String(length=128), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('session_id'),
    sa.UniqueConstraint('session_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('session')
    op.drop_table('offer')
    op.drop_table('message')
    op.drop_table('image')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    op.drop_table('tag')
    # ### end Alembic commands ###
