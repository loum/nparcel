import unittest2
import os
import tempfile

import nparcel


class TestMts(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._mts = nparcel.Mts(config='nparcel/conf/npmts.conf')
        cls._mts.set_template_dir('nparcel/templates')

    def test_init(self):
        """Initialise a MTS object.
        """
        msg = 'Object is not an nparcel.Mts'
        self.assertIsInstance(self._mts, nparcel.Mts, msg)

    def test_db_kwargs(self):
        """Verify the DB kwargs.
        """
        received = self._mts.db_kwargs()
        expected = {'host': 'host',
                    'user': 'user',
                    'password': 'password',
                    'port': 1521,
                    'sid': 'sid'}
        msg = 'Database kwargs error'
        self.assertDictEqual(received, expected, msg)

    def test_db_connection_string(self):
        """DB connection string.
        """
        received = self._mts.conn_string
        expected = 'user/password@host:1521/sid'
        msg = 'DB connection string error'
        self.assertEqual(received, expected, msg)

    def test_parse_config_items(self):
        """Verify required configuration items.
        """
        # Report range.
        msg = 'Report range error'
        received = self._mts.report_range
        expected = 7
        self.assertEqual(received, expected, msg)

        # Display headers.
        msg = 'Display headers error'
        received = self._mts.display_headers
        self.assertTrue(received, msg)

        # Output directory.
        msg = 'Report output directry error'
        received = self._mts.out_dir
        expected = '/data/nparcel/mts'
        self.assertEqual(received, expected, msg)

        # File cache.
        msg = 'File cache size error'
        received = self._mts.file_cache
        expected = 10
        self.assertEqual(received, expected, msg)

    def test_report_no_db_connection(self):
        """Generate a delivery report with no DB connection.
        """
        dry = False
        received = self._mts.report(dry=dry)
        msg = 'Report run with no DB connection should return None'
        self.assertIsNone(received, msg)

    def test_report(self):
        """Generate a delivery report.
        """
        dry = True
        if not dry:
            self._mts.set_report_range(1)
            self._mts.connect()

        received = self._mts.report(dry=dry)

        if not dry:
            self._mts.disconnect()

        msg = 'Report run should return a non-None filename string'
        self.assertIsNotNone(received, msg)

    def test_file_purge_no_files_exist(self):
        """File purge attempt with no files.
        """
        dir = tempfile.mkdtemp()
        old_out_dir = self._mts.out_dir
        self._mts.set_out_dir(dir)

        received = self._mts.purge_files()
        expected = []
        msg = 'File purge with no report files should return empty list'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._mts.set_out_dir(old_out_dir)
        os.removedirs(dir)

    def test_file_purge_no_directory_exist(self):
        """File purge attempt directory does not exist.
        """
        dir = tempfile.mkdtemp()
        old_out_dir = self._mts.out_dir
        self._mts.set_out_dir(dir)
        os.removedirs(dir)

        received = self._mts.purge_files()
        expected = []
        msg = 'File purge with no directory should return empty list'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._mts.set_out_dir(old_out_dir)

    def test_file_purge(self):
        """File purge attempt.
        """
        dir = tempfile.mkdtemp()
        old_out_dir = self._mts.out_dir
        self._mts.set_out_dir(dir)

        old_file_cache = self._mts.file_cache
        self._mts.set_file_cache(2)

        created_files = []
        for i in range(5):
            file = '%s%d.csv' % ('mts_delivery_report_2013101712000', i)
            f = open(os.path.join(dir, file), 'w')
            created_files.append(f.name)
            f.close()

        received = self._mts.purge_files(dry=False)
        expected = []
        msg = 'File purge with no report files should return empty list'
        #self.assertListEqual(received, expected, msg)

        # Clean up.
        for file in [x for x in created_files if x not in received]:
            os.remove(os.path.join(dir, file))

        self._mts.set_out_dir(old_out_dir)
        os.removedirs(dir)
        self._mts.set_file_cache(old_file_cache)

    @classmethod
    def tearUpClass(cls):
        cls._mts = None
        del cls._mts
