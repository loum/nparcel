import unittest2

import nparcel

FILE_BU = {'tolp': '1', 'tolf': '2', 'toli': '3'}
COND_MAP_IPEC = {'item_number_excp': True}
VALID_CONNOTE = '218501217863'
VALID_ITEM_NUMBER = 'abcdefghijklmnopqrstuvwxyz012345'
VALID = """218501217863          YMLML11TOLI130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                               abcdefghijklmnopqrstuvwxyz012345                                        HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
MISSING_BARCODE = """218501217863          YMLML11TOLI130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                                              N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                               abcdefghijklmnopqrstuvwxyz012345                                        HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
MISSING_CONNOTE = """                      YMLML11TOLI130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """
MISSING_ITEM = """218501217863          YMLML11TOLI130413  Diane Donohoe                           31 Bridge st,                 Lane Cove,                    Australia Other               2066                                                                                                                 Diane Donohoe                             Bally                         Hong Kong Other                                                               4156536111     N031                                                                                                                                   00001000001                                                                      Parcels Overnight                   Rm 603, Yeekuk Industrial,, 55Li chi kok, HK.                                                                                                      N031                                                                                                       HONG KONG                     AUSTRALIA                                                                                                                                                                                                      1  NS                                               """


class TestLoaderIpec(unittest2.TestCase):
    """Loader test cases specific to Ipec loader scenarios.
    """

    @classmethod
    def setUpClass(cls):
        cls._ldr = nparcel.Loader()
        cls._job_ts = cls._ldr.db.date_now()

    def test_processor_valid(self):
        """Process raw T1250 line -- missing barcode.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        msg = 'T1250 record should process OK'
        received = self._ldr.process(self._job_ts,
                                     VALID,
                                     FILE_BU.get('toli'),
                                     COND_MAP_IPEC)
        self.assertTrue(received, msg)

        # Check that the item_number value is honored.
        sql = """SELECT item_nbr
FROM job_item
WHERE connote_nbr = '%s'""" % VALID_CONNOTE
        self._ldr.db(sql)
        received = self._ldr.db.row
        expected = ('%s' % VALID_ITEM_NUMBER, )
        msg = ('Expected Item Number "%s" query not returned' %
               VALID_ITEM_NUMBER)
        self.assertEqual(received, expected, msg)

        # Restore DB state.
        self._ldr.db.connection.rollback()

    def test_processor_missing_barcode(self):
        """Process raw T1250 line -- missing barcode.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        msg = 'T1250 record with missing barcode should fail'
        received = self._ldr.process(self._job_ts,
                                     MISSING_BARCODE,
                                     FILE_BU.get('toli'),
                                     COND_MAP_IPEC)
        self.assertFalse(received, msg)

        # Restore DB state.
        self._ldr.db.connection.rollback()

    def test_processor_missing_connote(self):
        """Process raw T1250 line -- missing connote.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        msg = 'T1250 record with missing connote should fail'
        received = self._ldr.process(self._job_ts,
                                     MISSING_CONNOTE,
                                     FILE_BU.get('toli'),
                                     COND_MAP_IPEC)
        self.assertFalse(received, msg)

        # Restore DB state.
        self._ldr.db.connection.rollback()

    def test_processor_missing_item_number(self):
        """Process raw T1250 line -- missing item_number.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        msg = 'T1250 record with missing item_number should fail'
        received = self._ldr.process(self._job_ts,
                                     MISSING_ITEM,
                                     FILE_BU.get('toli'),
                                     COND_MAP_IPEC)
        self.assertFalse(received, msg)

        # Restore DB state.
        self._ldr.db.connection.rollback()

    @classmethod
    def tearDownClass(cls):
        cls._ldr = None
        cls._job_ts = None
