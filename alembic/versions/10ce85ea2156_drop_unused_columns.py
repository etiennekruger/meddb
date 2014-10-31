"""Drop unused columns.

Revision ID: 10ce85ea2156
Revises: 484ee9cd0c59
Create Date: 2014-08-18 14:58:58.251956

"""

# revision identifiers, used by Alembic.
revision = '10ce85ea2156'
down_revision = '484ee9cd0c59'

from alembic import op
import sqlalchemy as sa
from .utils import add_column_sqlite, drop_column_sqlite


def upgrade():
    drop_column_sqlite('medicine', 'alternative_names')
    drop_column_sqlite('procurement', 'unit_of_measure')
    pass


def downgrade():
    add_column_sqlite('medicine', sa.Column('alternative_names', sa.String))
    add_column_sqlite('procurement', sa.Column('unit_of_measure', sa.String))
    pass
