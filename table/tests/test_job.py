import unittest2
import os

import nparcel


class TestJob(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._job = nparcel.Job()
        cls._db = nparcel.DbSession()
        cls._db.connect()
        cls._db.create_table(name="job",
                             schema=cls._job.schema)

    def test_check_barcode(self):
        """Bar code check.
        """
        bc = '4156778061'
        sql = """
INSERT INTO job (card_ref_nbr)
VALUES ("%s")""" % bc
        self._db(sql)

        self._db(self._job.check_barcode(barcode=bc))
        received = []
        for row in self._db.rows():
            received.append(row[0])
        expected = [1]
        msg = 'Barcode value not returned from "job" table'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None
