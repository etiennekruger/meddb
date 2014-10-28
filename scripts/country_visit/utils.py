import csv
import operator


def sort_list(unsorted_list, key):
    """
    Sort a list of dicts by the value found with the key provided.
    """

    return sorted(unsorted_list, key=operator.itemgetter(key))


def add_commas(quantity):
    out = ""
    quantity_str = str(quantity)
    while len(quantity_str) > 3:
        tmp = quantity_str[-3::]
        out = " " + tmp + out
        quantity_str = quantity_str[0:-3]
    return quantity_str + out


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    """
    special csv reader, that handles unicode
    """
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8').strip() for cell in row]


def get_reader(filename):

    return unicode_csv_reader(open(filename, 'rU'), delimiter=',')


def map_data(headings, reader):
    """
    Convert the reader's list of rows and cells to a list of dicts.
    """

    recs = []
    for row in reader:
        rec = {}
        for i in range(len(headings)):
            val = row[i].strip()
            try:
                val = int(row[i])
            except ValueError:
                try:
                    val = float(row[i])
                except ValueError:
                    pass
                pass
            rec[headings[i]] = val
        recs.append(rec)

    # throw out the header row
    recs = recs[1::]
    return recs