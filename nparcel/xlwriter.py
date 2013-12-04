__all__ = [
    "Xlwriter",
]
import nparcel
from nparcel.utils.log import log
from nparcel.openpyxl import Workbook
from nparcel.openpyxl.style import Color, Fill


class Xlwriter(nparcel.Writer):
    """Toll Parcel Portal Writer class.

    """
    _title = None
    _subtitle = None

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

        ws.title = 'New Title Test'

        ws.merge_cells('A1:O1')
        cell = ws.cell('A1')
        cell.style.font.size = 20
        cell.style.font.bold = True
        cell.style.fill.fill_type = Fill.FILL_SOLID
        cell.style.fill.start_color.index = Color.LIGHTGREY
        cell.value = self.title

        ws.merge_cells('A2:O2')
        cell = ws.cell('A2')
        cell.style.font.size = 10
        cell.style.fill.fill_type = Fill.FILL_SOLID
        cell.style.fill.start_color.index = Color.LIGHTGREY
        cell.value = self.subtitle

        for column in range(15):
            cell = ws.cell(row=2, column=column)
            cell.style.fill.fill_type = Fill.FILL_SOLID
            cell.style.fill.start_color.index = Color.LIGHTBLUE
            cell.value = 'Heading %d' % column

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
