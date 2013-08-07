import unittest2
import datetime

import nparcel


class TestAgedParcelReporter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._apr = nparcel.AgedParcelReporter()

        now = datetime.datetime.now()
        # "aged_parcel_stocktake" table.
        aged_parcels = [{'created_ts': '%s' % now,
                         'scanned_item': 'SCANNED_01'},
                        {'created_ts': '%s' % now,
                         'scanned_item': 'SCANNED_02'},
                        {'created_ts': '%s' %
                         (now - datetime.timedelta(seconds=605000)),
                         'scanned_item': 'SCANNED_03'}]
        for aged_parcel in aged_parcels:
            sql = cls._apr.db._stocktake.insert_sql(aged_parcel)
            cls._apr.db(sql)

    def test_init(self):
        """AgedParcelReporter initialisation placeholder.
        """
        pass

    def test_aged_parcel_stocktake_sql(self):
        """Standard aged parcel query -- default age.
        """
        age = self._apr.age
        sql = self._apr.db.stocktake.aged_parcel_stocktake_sql(age)

        received = []
        self._apr.db(sql)
        for row in self._apr.db.rows():
            # Push the scanned_item.
            received.append(row[2])
        msg = 'Aged parcel list (default age) not as expected.'
        expected = ['SCANNED_03']
        self.assertListEqual(received, expected, msg)

    def test_aged_parcel_stocktake_sql_no_aged(self):
        """Standard aged parcel query -- increased age.
        """
        old_age = self._apr.age
        self._apr.set_age(800000)
        age = self._apr.age

        received = []
        for row in self._apr.get_aged_parcels():
            # Push the scanned_item.
            received.append(row[2])
        msg = 'Aged parcel list (increased age) not as expected.'
        expected = []
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._apr.set_age(old_age)

    @classmethod
    def tearDownClass(cls):
        cls._apr = None
