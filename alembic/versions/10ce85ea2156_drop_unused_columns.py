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


def drop_column_sqlite(tablename, column):
    """ column dropping functionality for SQLite """

    # we need copy to make a deep copy of the column attributes
    from copy import copy

    # get the db engine and reflect database tables
    engine = op.get_bind()
    meta = sa.MetaData(bind=engine)
    meta.reflect()

    # create a select statement from the old table
    old_table = meta.tables[tablename]
    select = sa.sql.select([c for c in old_table.c if c.name != column])

    # get remaining columns without table attribute attached
    remaining_columns = [copy(c) for c in old_table.columns
            if c.name != column]
    for column in remaining_columns:
        column.table = None
        # hack to retain NOT NULL constraints for the medicine table
        if tablename == 'medicine' and column.name in ['dosage_form_id', 'unit_of_measure_id']:
            column.nullable = False

    # create a temporary new table
    new_tablename = '{0}_new'.format(tablename)
    # hack to retain UNIQUE constraints for the medicine table
    if tablename == 'medicine':
        constraint = sa.UniqueConstraint('name', 'dosage_form_id', name='medicine_name_dosage_form')
        tmp = copy(remaining_columns)
        tmp.append(constraint)
        op.create_table(new_tablename, *tmp)
    else:
        op.create_table(new_tablename, *remaining_columns)
    meta.reflect()
    new_table = meta.tables[new_tablename]

    # copy data from old table
    insert = sa.sql.insert(new_table).from_select(
            [c.name for c in remaining_columns], select)
    engine.execute(insert)

    # drop the old table and rename the new table to take the old tables
    # position
    op.drop_table(tablename)
    op.rename_table(new_tablename, tablename)


def upgrade():
    drop_column_sqlite('medicine', 'alternative_names')
    drop_column_sqlite('procurement', 'unit_of_measure')
    pass


def downgrade():
    op.add_column('medicine', sa.Column('alternative_names', sa.String))
    op.add_column('procurement', sa.Column('unit_of_measure', sa.String))
    pass
