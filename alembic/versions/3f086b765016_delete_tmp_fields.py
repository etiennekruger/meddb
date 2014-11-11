"""delete tmp fields

Revision ID: 3f086b765016
Revises: 1e9417ec75e
Create Date: 2014-11-11 16:10:23.668756

"""

# revision identifiers, used by Alembic.
revision = '3f086b765016'
down_revision = '1e9417ec75e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('procurement', 'tmp_approved')
    op.drop_column('product', 'tmp_is_generic')
    op.drop_column('registration', 'tmp_expired')
    op.drop_column('supplier', 'tmp_authorized')
    op.drop_column('user', 'tmp_is_admin')
    op.drop_column('user', 'tmp_activated')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('tmp_activated', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('tmp_is_admin', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('supplier', sa.Column('tmp_authorized', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('registration', sa.Column('tmp_expired', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('product', sa.Column('tmp_is_generic', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('procurement', sa.Column('tmp_approved', sa.BOOLEAN(), autoincrement=False, nullable=True))
    ### end Alembic commands ###
