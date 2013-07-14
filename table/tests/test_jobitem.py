import unittest2

import nparcel


class TestJobItem(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._job_item = nparcel.JobItem()
        cls._db = nparcel.DbSession()
        cls._db.connect()
        cls._db.create_table(name="job_item",
                             schema=cls._job_item.schema)

    def test_init(self):
        """Placeholder test to make sure the "job_item" table is created.
        """
        pass

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None
