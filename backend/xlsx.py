import xlsxwriter
import StringIO
from datetime import datetime
from dateutil.parser import parse
from backend import logger


def procurements_to_excel(procurements):

    headings = [
        "Medicine",
        "Dosage Form",
        "Description",
        "Start Date",
        "End Date",
        "Pack Size",
        "Unit of Measure",
        "Container",
        "Quantity",
        "Pack Price",
        "Unit Price",
        "Incoterm",
        "Manufacturer",
        "Supplier",
        ]

    list_out = [headings,]
    for procurement in procurements:
        procurement = procurement.to_dict(include_related=True)
        cells = []
        cells.append(str(procurement['product']['medicine']['name']))
        cells.append(str(procurement['product']['medicine']['dosage_form']['name']))
        cells.append(str(procurement['product']['description']))
        cells.append(str(procurement['start_date']))
        cells.append(str(procurement['end_date']))
        cells.append(str(procurement['pack_size']))
        cells.append(str(procurement['product']['medicine']['unit_of_measure']))
        cells.append(str(procurement['container']))
        cells.append(str(procurement['quantity']))
        cells.append(str(procurement['pack_price_usd']))
        cells.append(str(procurement['unit_price_usd']))
        if procurement.get('incoterm'):
            cells.append(procurement['incoterm']['code'])
        else:
            cells.append("")
        if procurement.get('supplier'):
            cells.append(str(procurement['supplier']['name']))
        else:
            cells.append("")
        if procurement['product'].get('manufacturer'):
            cells.append(str(procurement['product']['manufacturer']['name']))
        else:
            cells.append("")
        list_out.append(cells)

    return list_out


class XLSXBuilder:
    def __init__(self, procurements):
        self.procurements = procurements
        self.formats = {}

    def build(self):
        """
        Generate an Excel spreadsheet and return it as a string.
        """
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)

        self.formats['date'] = workbook.add_format({'num_format': 'yyyy/mm/dd'})
        self.formats['bold'] = workbook.add_format({'bold': True})

        self.procurements_worksheet(workbook)

        workbook.close()
        output.seek(0)

        return output.read()

    def procurements_worksheet(self, wb):
        ws = wb.add_worksheet('procurements')
        tmp = procurements_to_excel(self.procurements)
        self.write_table(ws, 'Procurements', tmp)

    def write_table(self, ws, name, rows, keys=None, rownum=0, colnum=0):
        if rows:
            keys = rows[0]
            data = rows

            ws.add_table(rownum, colnum, rownum+len(rows), colnum+len(keys)-1, {
                'name': name,
                'columns': [{'header': k} for k in keys],
                'data': data,
                })

        return len(rows)+1
