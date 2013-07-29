import unittest2
import datetime
import tempfile
import os

import nparcel


class TestExporter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._e = nparcel.Exporter()

        now = datetime.datetime.now()
        jobitems = [{'connote_nbr': '218501217863',
                     'pickup_ts': '%s' % now,
                     'pod_name': 'pod_name 218501217863',
                     'identity_type_data': 'identity 218501217863'},
                    {'connote_nbr': '218501217864',
                     'pickup_ts': '%s' %
                     (now - datetime.timedelta(seconds=86400)),
                     'pod_name': 'pod_name 218501217864',
                     'identity_type_data': 'identity 218501217864'},
                    {'connote_nbr': '218501217865',
                     'pickup_ts': '%s' %
                     (now - datetime.timedelta(seconds=(86400 * 2))),
                     'pod_name': 'pod_name 218501217865',
                     'identity_type_data': 'identity 218501217865'}]
        for jobitem in jobitems:
            sql = cls._e.db.jobitem.insert_sql(jobitem)
            jobitem_id = cls._e.db.insert(sql=sql)

        # Create a temporary directory structure.
        cls._dir = tempfile.mkdtemp()

    def test_init(self):
        """Initialise an Exporter object.
        """
        msg = 'Object is not an nparcel.Exporter'
        self.assertIsInstance(self._e, nparcel.Exporter, msg)

    def test_collected_sql_one_day_range(self):
        """One day range collection check.
        """
        msg = 'One day range collection check should return results.'
        sql = self._e.db.jobitem.collected_sql(range=86400)
        self._e.db(sql)

        received = []
        for row in self._e.db.rows():
            received.append(row[0])

        # Loose check should return values.
        self.assertTrue(received, msg)

    def test_collected_sql_beyond_range(self):
        """Range beyond collection check.
        """
        msg = 'Default collection check should return results.'
        sql = self._e.db.jobitem.collected_sql(range=-1)
        self._e.db(sql)

        received = []
        for row in self._e.db.rows():
            received.append(row[0])

        # Loose check should return NO values.
        self.assertFalse(received, msg)

    def test_cached_items_if_file_not_provided(self):
        """Check cached items if a cache file is not provided.
        """
        msg = "Collected items with no cache should not be None"
        self._e.get_collected_items()
        self.assertIsNotNone(self._e._collected_items, msg)

    def test_report(self):
        """Verify reporter output.
        """
        # Regenerate the collected items list.
        del self._e._collected_items[:]
        self._e.get_collected_items()
        self._e.report()

    def test_cleansed_valid_date(self):
        """Cleanse valid data.
        """
        row = ('', '', '2013-07-29 12:00:00.123456', '', '', '')
        received = self._e._cleanse(row)
        expected = ('', '', '2013-07-29 12:00:00', '', '', '')
        msg = 'Cleansed valid data incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_cleansed_invalid_date(self):
        """Cleanse invalid pickup_ts data.
        """
        row = ('', '', '2013-07-29 12:00:00', '', '', '')
        received = self._e._cleanse(row)
        expected = ('', '', '2013-07-29 12:00:00', '', '', '')
        msg = 'Cleansed valid data incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_output_file_creation(self):
        """Output file handle creation.
        """
        staging = os.path.join(self._dir, 'staging')

        msg = 'Export reporting file handle should not be None'
        fh = self._e.outfile(staging)
        self.assertIsNotNone(fh, msg)

        outfile = fh.name
        fh.close()

        # Cleanup.
        os.remove(outfile)
        os.rmdir(staging)

    def test_output_file_write(self):
        """Output file write.
        """
        staging = os.path.join(self._dir, 'staging')

        # Regenerate the collected items list.
        del self._e._collected_items[:]

        self._e.set_staging_dir(staging)
        self._e.get_collected_items()
        file_name = self._e.report()

        # Restore and cleanup.
        os.remove(file_name.replace('.txt.tmp', '.txt'))
        os.rmdir(staging)
        self._e.set_staging_dir(None)

    @classmethod
    def tearDownClass(cls):
        cls._r = None
        os.removedirs(cls._dir)
