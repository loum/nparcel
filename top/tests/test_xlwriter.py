import unittest2
import tempfile
import os

import nparcel

from nparcel.utils.files import remove_files


class TestXlwriter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._x = nparcel.Xlwriter()
        cls._dir = tempfile.mkdtemp()

    def test_init(self):
        """Initialise a Xlwriter object.
        """
        msg = 'Object is not an nparcel.Xlwriter'
        self.assertIsInstance(self._x, nparcel.Xlwriter, msg)

    def test_write(self):
        """Write out the headers and content.
        """
        rep_title = 'Toll Parcel Portal Stocktake Uncollected (Aged) Report'
        self._x.set_title(rep_title)

        sub_title = 'ITEMS UNCOLLECTED FOR MORE THAN 7 DAYS'
        self._x.set_subtitle(sub_title)

        ws_title = 'Uncollected'
        self._x.set_worksheet_title(ws_title)

        headers = ['Agent',
                   'Agent Name',
                   'Business Unit',
                   'Connote',
                   'Item Nbr',
                   'To',
                   'Pieces']
        self._x.set_headers(headers)

        header_widths = {'Agent Name': 30,
                         'Connote': 40,
                         'Item Nbr': 50,
                         'To': 30}
        self._x.set_header_widths(header_widths)

        file = os.path.join(self._dir, 'test.xlsx')
        self._x.set_outfile(file)

        data = [('VIC999',
                 'VIC Test Newsagent 999',
                 1,
                 'TEST_REF_01',
                 '003934032500820300xx',
                 'Con Sumertwenty',
                 20),
                ('NSW999',
                 'NSW Test Newsagent 999',
                 2,
                 'TEST_REF_02',
                 '003934032500820300yy',
                 'Con Sumertwentyone',
                  21)]
        self._x(data)

        # Clean up.
        remove_files(file)

    @classmethod
    def tearDownClass(cls):
        cls._x = None
        del cls._x
        os.removedirs(cls._dir)
        cls._dir = None
        del cls._dir
