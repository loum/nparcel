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
                         'scanned_item': 'SCANNED_03'},
                        {'created_ts': '%s' % now,
                         'scanned_item': 'DODGY_01'}]
        for aged_parcel in aged_parcels:
            sql = cls._apr.db._stocktake.insert_sql(aged_parcel)
            cls._apr.db(sql)

        # "job_items" table.
        jobitems = [{'connote_nbr': 'SCANNED_01',
                     'created_ts': '%s' %
                     (now - datetime.timedelta(seconds=605000)),
                     'pod_name': 'pod_name SCANNED_01',
                     'identity_type_data': 'identity SCANNED_01'}]
        for jobitem in jobitems:
            sql = cls._apr.db.jobitem.insert_sql(jobitem)
            jobitem_id = cls._apr.db.insert(sql=sql)

    def test_init(self):
        """AgedParcelReporter initialisation placeholder.
        """
        pass

    def test_aged_parcel_stocktake_sql(self):
        """Aged parcel query -- default age.
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

    def test_aged_parcel_stocktake_sql_extended_aged(self):
        """Aged parcel query -- extended age.
        """
        old_age = self._apr.age
        self._apr.set_age(800000)

        received = []
        for row in self._apr.get_aged_parcels():
            # Push the scanned_item.
            received.append(row[2])
        msg = 'Aged parcel list (increased age) not as expected.'
        expected = []
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._apr.set_age(old_age)

    def test_aged_parcel_stocktake_sql_no_age(self):
        """Aged parcel query -- no age.
        """
        old_age = self._apr.age
        self._apr.set_age(None)

        received = []
        for row in self._apr.get_aged_parcels():
            # Push the scanned_item.
            received.append(row[2])
        msg = 'Aged parcel list (no age) not as expected.'
        expected = ['SCANNED_01',
                    'SCANNED_02',
                    'SCANNED_03',
                    'DODGY_01']
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._apr.set_age(old_age)

    def test_aged_jobitem_sql_no_age(self):
        """Aged jobitem query -- default age.
        """
        received = []
        for row in self._apr.get_aged_jobitems():
            # Push the connote_nbr.
            received.append(row[2])
        msg = "Aged jobitem's not as expected"
        expected = ['SCANNED_01']
        self.assertListEqual(received, expected, msg)

    def test_get_aged(self):
        """Aged parcels.
        """
        received = []
        for row in self._apr.get_aged():
            # Push the connote_nbr.
            received.append(row[2])
        msg = "Aged parcels not as expected"
        expected = ['SCANNED_01']
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._apr = None
