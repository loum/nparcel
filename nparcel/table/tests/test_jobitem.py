import unittest2
import datetime

import nparcel


class TestJobItem(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._job_item = nparcel.JobItem()
        cls._db = nparcel.DbSession()
        cls._db.connect()

    def test_jobitem_table_insert_with_valid_nparcel_data(self):
        """Insert valid Nparcel data into "job_item" table.
        """
        kwargs = {'connote_nbr': '218501217863',
                  'consumer_name': 'Diane Donohoe',
                  'pieces': '00001',
                  'status': 1,
                  'created_ts': datetime.datetime.now().isoformat()}
        received = self._db.insert(self._job_item.insert_sql(kwargs))
        expected = 1
        msg = '"job_item" table insert returned unexpected row_id'
        self.assertEqual(received, expected, msg)

        self._db.connection.rollback()

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None