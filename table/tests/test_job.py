import unittest2
import os

import nparcel

JOB_SCHEMA = """
CREATE TABLE job (
    id INTEGER PRIMARY KEY,
    card_ref_nbr CHAR(15))"""


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
        sql = """
INSERT INTO job (card_ref_nbr)
VALUES ('4156778061')"""
        self._db(sql)

        sql = """SELECT * FROM job"""
        self._db(sql)
        received = []
        for row in self._db.rows():
            received.append(row[1])
        expected = ['4156778061']
        msg = 'Barcode value not returned from "job" table'
        self.assertListEqual(expected, received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None
