"""Add FOB price columns.

Revision ID: 3a36cf873257
Revises: 10ce85ea2156
Create Date: 2014-10-31 10:56:29.448254

"""

# revision identifiers, used by Alembic.
revision = '3a36cf873257'
down_revision = '10ce85ea2156'

from alembic import op
import sqlalchemy as sa
from .utils import add_column_sqlite, drop_column_sqlite


def upgrade():
    add_column_sqlite('country', 'default_fob_adjustment')
    add_column_sqlite('procurement', 'unit_price_usd_fob')
    pass


def downgrade():
    drop_column_sqlite('country', 'default_fob_adjustment')
    drop_column_sqlite('procurement', 'unit_price_usd_fob')
    pass
