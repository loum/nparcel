import unittest2
import datetime

import nparcel


class TestAgentParcelStocktake(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._aps = nparcel.AgentParcelStocktake()
        cls._db = nparcel.DbSession()
        cls._db.connect()
        cls._created_ts = datetime.datetime.now().isoformat(' ')[:-3]

    def test_insert(self):
        """Insert valid Nparcel stocktake item.
        """
        kwargs = {'created_ts': self._created_ts,
                  'scanned_item': 'BANANASCAN'}
        self._db(self._aps.insert_sql(kwargs))

    @classmethod
    def tearDownClass(cls):
        cls._aps = None
        cls._db.close()
        cls._db = None
        cls._created_ts = None
