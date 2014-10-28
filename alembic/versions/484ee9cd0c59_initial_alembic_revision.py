"""Initial alembic revision.

Revision ID: 484ee9cd0c59
Revises: None
Create Date: 2014-08-18 14:45:12.442432

"""

# revision identifiers, used by Alembic.
revision = '484ee9cd0c59'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.drop_table('ingredient')
    op.drop_table('component')
    pass


def downgrade():
    pass
