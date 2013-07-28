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

    def test_collected_sql_default(self):
        """Default collection check.
        """
        msg = 'Default collection check should return results.'
        sql = self._e.db.jobitem.collected_sql()
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

    @classmethod
    def tearDownClass(cls):
        cls._r = None
