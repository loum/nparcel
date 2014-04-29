__all__ = [
    "Xlwriter",
]
import datetime

import top
from top.utils.log import log
from top.openpyxl import Workbook
from top.openpyxl.style import Color, Fill, Border
from top.openpyxl.cell import get_column_letter

Color.LIGHTBLUE = 'FFB5DAFF'
Color.LIGHTERBLUE = 'FFE9F4FF'
Color.LIGHTGREY = 'FFD1D1D1'
Color.REALLYLIGHTGREY = 'FFF1F1F1'


class Xlwriter(top.Writer):
    """Toll Outlet Portal Writer class.

    .. attribute:: title

        report title that is presented with more pronounced font

    .. attribute:: subtitle

        second level title

    .. attribute:: worksheet_title

        title that will appear on the current worksheet tab

    .. attribute:: headers

        data column headers

    .. attribute:: date

        string representation of date and time.  Typically used to
        capture when the report was run

    """
    _title = None
    _subtitle = None
    _worksheet_title = None
    _headers = []
    _header_widths = {}
    _date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    def __init__(self, outfile=None):
        """Writer initialiser.

        """
        super(top.Xlwriter, self).__init__(outfile=outfile)

    def __call__(self, data):
        """Class callable that writes list of tuple values in *data*.

        **Args:**
            *data*: list of tuples to write out

        """
        wb = Workbook()
        ws = wb.get_active_sheet()

        ws.title = self.worksheet_title

        # Main title.
        row = 0
        end_column = len(self.headers) - 1
        if end_column < 0:
            end_column = 0
        ws.merge_cells(start_row=row,
                       start_column=0,
                       end_row=row,
                       end_column=end_column)
        cell = ws.cell(row=row, column=0)
        cell.style.font.size = 20
        cell.style.font.bold = True
        cell.style.fill.fill_type = Fill.FILL_SOLID
        cell.style.fill.start_color.index = Color.LIGHTGREY
        cell.value = self.title
        row += 1

        # Subtitle.
        sub_title_end_column = end_column - 2
        if sub_title_end_column < 0:
            sub_title_end_column = 0
        ws.merge_cells(start_row=row,
                       start_column=0,
                       end_row=row,
                       end_column=sub_title_end_column)
        cell = ws.cell(row=row, column=0)
        cell.style.font.size = 10
        cell.style.fill.fill_type = Fill.FILL_SOLID
        cell.style.fill.start_color.index = Color.LIGHTGREY
        cell.value = self.subtitle

        # Date
        ws.merge_cells(start_row=row,
                       start_column=sub_title_end_column + 1,
                       end_row=row,
                       end_column=end_column)
        cell = ws.cell(row=row, column=sub_title_end_column + 1)
        cell.style.font.size = 10
        cell.style.fill.fill_type = Fill.FILL_SOLID
        cell.style.fill.start_color.index = Color.LIGHTGREY
        cell.value = 'Report Date: %s' % self.date
        row += 1

        # Headers.
        for column in range(len(self.headers)):
            cell = ws.cell(row=row, column=column)
            cell.style.fill.fill_type = Fill.FILL_SOLID
            cell.style.fill.start_color.index = Color.LIGHTBLUE
            cell.style.borders.bottom.border_style = Border.BORDER_THIN
            cell.value = self.headers[column]
        row += 1

        # Data.
        for data_item in data:
            for row_index in range(len(data_item)):
                v = data_item[row_index]
                cell = ws.cell(row=row, column=row_index)
                if not (row % 2):
                    cell.style.fill.fill_type = Fill.FILL_SOLID
                    cell.style.fill.start_color.index = Color.LIGHTERBLUE
                cell.value = v

            row += 1

        # Column Dimensions.
        for column in range(len(self.headers)):
            hdr = self.headers[column]
            hdr_length = self.header_widths.get(hdr.lower())
            column_letter = get_column_letter(column + 1)
            if hdr_length is not None:
                ws.column_dimensions[column_letter].width = hdr_length

        # Summary.
        row += 1
        ws.merge_cells(start_row=row,
                       start_column=0,
                       end_row=row,
                       end_column=2)

        for column in range(len(self.headers)):
            cell = ws.cell(row=row, column=column)
            cell.style.fill.fill_type = Fill.FILL_SOLID
            cell.style.fill.start_color.index = Color.REALLYLIGHTGREY
            cell.style.borders.bottom.border_style = Border.BORDER_DOUBLE
        cell = ws.cell(row=row, column=0)
        cell.style.font.bold = True
        cell.value = 'Total: %d' % len(data)
        ws.row_dimensions[row + 1].height = 20

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
        log.debug('Setting report subtitle to "%s"' % str(value))
        self._subtitle = value

    @property
    def worksheet_title(self):
        return self._worksheet_title

    def set_worksheet_title(self, value=None):
        log.debug('Setting worksheet title to "%s"' % str(value))
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

    @property
    def date(self):
        return self._date

    def set_date(self, value=None):
        log.debug('Setting date to "%s"' % str(value))
        self._date = value
