import unittest2
import tempfile
import datetime
import os

import top
from top.utils.files import remove_files


class TestWriter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._w = top.Writer()
        cls._dir = tempfile.mkdtemp()

    def test_init(self):
        """Initialise a Writer object.
        """
        msg = 'Object is not an top.Writer'
        self.assertIsInstance(self._w, top.Writer, msg)

    def test_write(self):
        """Write out the headers and content.
        """
        hdrs = ['JOB_ITEM_ID',
                'JOB_BU_ID',
                'CONNOTE_NBR',
                'BARCODE',
                'ITEM_NBR',
                'JOB_TS',
                'CREATED_TS',
                'NOTIFY_TS',
                'PICKUP_TS',
                'PIECES',
                'CONSUMER_NAME',
                'DP_CODE',
                'AGENT_NAME']
        self._w.set_headers(hdrs)

        data = expected = [(20,
                            1,
                            '="TEST_REF_NOT_PROC"',
                            '="aged_parcel_unmatched"',
                            '="00393403250082030047"',
                            '="%s"' % self._now,
                            '="%s"' % self._now,
                            None,
                            None,
                            20,
                            'Con Sumertwenty',
                            'VIC999',
                            'VIC Test Newsagent 999'),
                           (22,
                            1,
                            '="ARTZ061184"',
                            '="JOB_TEST_REF_NOT_PROC_PCKD_UP"',
                            '="00393403250082030048"',
                            '="%s"' % self._now,
                            '="%s"' % self._now,
                            None,
                            None,
                            22,
                            'Con Sumertwentytwo',
                            'VIC999',
                            'VIC Test Newsagent 999')]

        file = os.path.join(self._dir, 'test.csv')
        self._w.set_outfile(file)

        self._w(data)

        # Clean up.
        remove_files(file)

    def test_filter(self):
        """Filter columns to display.
        """
        hdrs = ['JOB_ITEM_ID',
                'JOB_BU_ID',
                'CONNOTE_NBR',
                'BARCODE',
                'ITEM_NBR',
                'JOB_TS',
                'CREATED_TS',
                'NOTIFY_TS',
                'PICKUP_TS',
                'PIECES',
                'CONSUMER_NAME',
                'DP_CODE',
                'AGENT_NAME']
        hdrs_to_display = ['DP_CODE',
                           'AGENT_NAME',
                           'JOB_BU_ID',
                           'CONNOTE_NBR',
                           'ITEM_NBR',
                           'CONSUMER_NAME',
                           'PIECES']
        data = (20,
                1,
                '="TEST_REF_NOT_PROC"',
                '="aged_parcel_unmatched"',
                '="00393403250082030047"',
                '="%s"' % self._now,
                '="%s"' % self._now,
                None,
                None,
                20,
                'Con Sumertwenty',
                'VIC999',
                'VIC Test Newsagent 999')

        received = self._w.filter(headers=hdrs,
                                  headers_displayed=hdrs_to_display,
                                  row=data)
        expected = ('VIC999',
                    'VIC Test Newsagent 999',
                    1,
                    '="TEST_REF_NOT_PROC"',
                    '="00393403250082030047"',
                    'Con Sumertwenty',
                    20)
        msg = 'Filtered row error'
        self.assertTupleEqual(received, expected, msg)

    def test_header_aliases(self):
        """Substitue header aliases.
        """
        hdrs_to_display = ['DP_CODE',
                           'AGENT_NAME',
                           'JOB_BU_ID',
                           'CONNOTE_NBR',
                           'ITEM_NBR',
                           'CONSUMER_NAME',
                           'PIECES']
        aliases = {'DP_CODE': 'Agent',
                   'AGENT_NAME': 'Agent Name',
                   'JOB_BU_ID': 'Business Unit',
                   'CONNOTE_NBR': 'Connote',
                   'ITEM_NBR': 'Item Nbr',
                   'PIECES': 'Pieces'}

        received = self._w.header_aliases(headers_displayed=hdrs_to_display,
                                          header_aliases=aliases)
        expected = ['Agent',
                    'Agent Name',
                    'Business Unit',
                    'Connote',
                    'Item Nbr',
                    'CONSUMER_NAME',
                    'Pieces']
        msg = 'Header alias substitution error'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._w = None
        del cls._w
        os.removedirs(cls._dir)
        cls._dir = None
        del cls._dir
