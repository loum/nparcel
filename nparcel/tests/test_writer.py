import unittest2
import tempfile
import datetime
import os

import nparcel
from nparcel.utils.files import remove_files


class TestWriter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._w = nparcel.Writer()
        cls._dir = tempfile.mkdtemp()

    def test_init(self):
        """Initialise a Writer object.
        """
        msg = 'Object is not an nparcel.Writer'
        self.assertIsInstance(self._w, nparcel.Writer, msg)

    def test_header_write(self):
        """Write out the headers.
        """
        hdrs = ['JOB_ITEM_ID',
                'JOB_BU_ID',
                'ji.connote_nbr',
                'j.card_ref_nbr',
                'ji.item_nbr',
                'j.job_ts',
                'ji.created_ts',
                'ji.notify_ts',
                'ji.pickup_ts',
                'ji.pieces',
                'ji.consumer_name',
                'ag.dp_code', 'ag.name']
        self._w.set_headers(hdrs)

        data = expected = [(20,
                            1,
                            'TEST_REF_NOT_PROC',
                            'aged_parcel_unmatched',
                            '00393403250082030047',
                            '%s' % self._now,
                            '%s' % self._now,
                            None,
                            None,
                            20,
                            'Con Sumertwenty',
                            'VIC999',
                            'VIC Test Newsagent 999'),
                           (22,
                            1,
                            'ARTZ061184',
                            'JOB_TEST_REF_NOT_PROC_PCKD_UP',
                            '00393403250082030048',
                            '%s' % self._now,
                            '%s' % self._now,
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

    @classmethod
    def tearDownClass(cls):
        cls._w = None
        del cls._w
        cls._dir = None
        del cls._dir
