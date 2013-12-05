__all__ = [
    "Xlwriter",
]
import nparcel
from nparcel.utils.log import log
from nparcel.openpyxl import Workbook
from nparcel.openpyxl.style import Color, Fill, Border
from nparcel.openpyxl.cell import get_column_letter

Color.REALLYLIGHTBLUE = 'FFD3E9FF'
Color.LIGHTGREY = 'FFD1D1D1'
Color.LIGHTBLUE = 'FFB5DAFF'


class Xlwriter(nparcel.Writer):
    """Toll Parcel Portal Writer class.

    """
    _title = None
    _subtitle = None
    _worksheet_title = None
    _headers = []
    _header_widths = {}

    def __init__(self, outfile=None):
        """Writer initialiser.

        """
        super(nparcel.Xlwriter, self).__init__(outfile=outfile)

    def __call__(self, data):
        """Class callable that writes list of tuple values in *data*.

        **Args:**
            *data*: list of tuples to write out

        """
        wb = Workbook()
        ws = wb.get_active_sheet()

        ws.title = self.worksheet_title

        # Main title.
        end_column = len(self.headers) - 1
        ws.merge_cells(start_row=0,
                       start_column=0,
                       end_row=0,
                       end_column=end_column)
        cell = ws.cell('A1')
        cell.style.font.size = 20
        cell.style.font.bold = True
        cell.style.fill.fill_type = Fill.FILL_SOLID
        cell.style.fill.start_color.index = Color.LIGHTGREY
        cell.value = self.title

        # Main subtitle.
        ws.merge_cells(start_row=1,
                       start_column=0,
                       end_row=1,
                       end_column=end_column)
        cell = ws.cell('A2')
        cell.style.font.size = 10
        cell.style.fill.fill_type = Fill.FILL_SOLID
        cell.style.fill.start_color.index = Color.LIGHTGREY
        cell.value = self.subtitle

        # Headers.
        for column in range(len(self.headers)):
            cell = ws.cell(row=2, column=column)
            cell.style.fill.fill_type = Fill.FILL_SOLID
            cell.style.fill.start_color.index = Color.LIGHTBLUE
            cell.style.borders.bottom.border_style = Border.BORDER_THIN
            cell.value = self.headers[column]

        # Data.
        #for row in rows:
        #    cell.style.fill.fill_type = Fill.FILL_SOLID
        #    cell.style.fill.start_color.index = Color.REALLYLIGHTBLUE

        # Column Dimensions.
        for column in range(len(self.headers)):
            h = self.headers[column]
            l = self.header_widths.get(h)
            column_letter = get_column_letter(column + 1)
            if l is not None:
                ws.column_dimensions[column_letter].width = l

        if self.outfile is not None:
            log.info('Preparing "%s" for output' % self.outfile)
            wb.save(self.outfile)
        else:
            log.warn('Report output file not defined -- skip write')

    @property
    def title(self):
        return self._title

    def set_title(self, value=None):
        log.debug('Setting report title to "%s"' % value)
        self._title = value

    @property
    def subtitle(self):
        return self._subtitle

    def set_subtitle(self, value=None):
        log.debug('Setting report subtitle to "%s"' % value)
        self._subtitle = value

    @property
    def worksheet_title(self):
        return self._worksheet_title

    def set_worksheet_title(self, value=None):
        log.debug('Setting worksheet title to "%s"' % value)
        self._worksheet_title = value

    @property
    def headers(self):
        return self._headers

    def set_headers(self, values=None):
        del self._headers[:]
        self._headers = []

        if values is not None:
            log.debug('Setting headers to "%s"' % str(values))
            self._headers.extend(values)

    @property
    def header_widths(self):
        return self._header_widths

    def set_header_widths(self, values=None):
        self._header_widths.clear()

        if values is not None:
            log.debug('Setting header_widths to "%s"' % str(values))
            self._header_widths = values
