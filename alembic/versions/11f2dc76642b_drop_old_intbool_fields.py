"""drop old intbool fields

Revision ID: 11f2dc76642b
Revises: 5881fb8f58e9
Create Date: 2014-11-11 15:39:57.034436

"""

# revision identifiers, used by Alembic.
revision = '11f2dc76642b'
down_revision = '5881fb8f58e9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('procurement', 'approved')
    op.drop_column('product', 'is_generic')
    op.drop_column('registration', 'expired')
    op.drop_column('supplier', 'authorized')
    op.drop_column('user', 'is_admin')
    op.drop_column('user', 'activated')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('activated', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('is_admin', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('supplier', sa.Column('authorized', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('registration', sa.Column('expired', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('product', sa.Column('is_generic', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('procurement', sa.Column('approved', sa.INTEGER(), autoincrement=False, nullable=True))
    ### end Alembic commands ###