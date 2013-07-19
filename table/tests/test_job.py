import unittest2
import datetime

import nparcel


class TestJob(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._job = nparcel.Job()
        cls._db = nparcel.DbSession()
        cls._db.connect()
        cls._job_ts = datetime.datetime.now().isoformat()

    def test_check_barcode(self):
        """Bar code check.
        """
        bc = '4156778061'
        fields = {'card_ref_nbr': bc,
                  'job_ts': self._job_ts}
        sql = """
INSERT INTO job (card_ref_nbr, job_ts)
VALUES ("%s", "%s")""" % (bc, self._job_ts)
        self._db(sql)

        self._db(self._job.check_barcode(barcode=bc))
        received = []
        for row in self._db.rows():
            received.append(row[0])
        expected = [1]
        msg = 'Barcode value not returned from "job" table'
        self.assertListEqual(received, expected, msg)

    def test_job_table_insert_with_valid_nparcel_data(self):
        """Insert valid Nparcel data.
        """
        kwargs = {'address_1': '31 Bridge st,',
                  'address_2': 'Lane Cove,',
                  'agent_id': 'N031',
                  'bu_id': 1,
                  'card_ref_nbr': '4156536111',
                  'job_ts': self._job_ts,
                  'status': 1,
                  'suburb': 'Australia Other'}
        self._db(self._job.insert_sql(kwargs))

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None
        cls._job = None
        cls._job_ts = None
