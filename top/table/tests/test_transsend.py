import unittest2
import os

import top


class TestTransSend(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._transsend = top.TransSend()
        cls._db = top.OraDbSession()
        cls._db.connect()
        cls._db.create_table(name='v_nparcel_adp_connotes',
                             schema=cls._db.transsend.schema)
        fixture_file = os.path.join('top',
                                    'tests',
                                    'fixtures',
                                    'transsend.py')
        cls._db.load_fixture(cls._db.transsend, fixture_file)

    def test_init(self):
        """TransSend table initialisation.
        """
        msg = 'Object is not a TransSend instance'
        self.assertIsInstance(self._transsend, top.TransSend, msg)

    def test_connote_sql(self):
        """Verify teh connote_sql string.
        """
        connote = 'APLD029228'
        item_nbr = 'APLD029228001'

        # Check the query via SQL.
        sql = self._db.transsend.connote_sql(connote_nbr=connote,
                                             item_nbr=item_nbr)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [(4,
                     'APLD029228',
                     '19102',
                     'APLD029228001',
                     'ON FOR DEL',
                     None,
                     None,
                     '2013-05-28 00:00:00',
                     '2013-05-27 14:34:25',
                     'DEL',
                     'Unresolved')]
        msg = 'TransSend job_item.connote return value not as expected'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._transsend = None
        del cls._transsend
        cls._db.disconnect()
        cls._db = None
