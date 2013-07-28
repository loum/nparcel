import unittest2
import datetime

import nparcel


class TestExporter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._e = nparcel.Exporter()

        now = datetime.datetime.now()
        jobitems = [{'pickup_ts': '%s' % now},
                    {'pickup_ts': '%s' %
                     (now - datetime.timedelta(seconds=86400))},
                    {'pickup_ts': '%s' %
                     (now - datetime.timedelta(seconds=(86400 * 2)))}]
        for jobitem in jobitems:
            sql = cls._e.db.jobitem.insert_sql(jobitem)
            jobitem_id = cls._e.db.insert(sql=sql)

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

    @classmethod
    def tearDownClass(cls):
        cls._r = None
