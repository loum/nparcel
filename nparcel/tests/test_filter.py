import unittest2

import nparcel


class TestFilter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        test_conf = 'nparcel/tests/test_loader.conf'
        cls._c = nparcel.Config(config_file=test_conf)
        cls._f = nparcel.Filter()

    def test_init(self):
        """Initialise a Filter object.
        """
        msg = 'Object is not an nparcel.Filter'
        self.assertIsInstance(self._f, nparcel.Filter, msg)

    def test_process_valid_record_parcel_point(self):
        """Process valid record.
        """
        line = self._c.get('test_lines', 'PP')
        received = self._f.process(line)
        msg = 'Valid ParcelPoint record should return True'
        self.assertTrue(received, msg)

    def test_process_missing_agent_id(self):
        """Process valid record -- missing Agent Id.
        """
        line = self._c.get('test_lines', 'PP_MISSING_AGENT_ID')
        received = self._f.process(line)
        msg = 'Valid ParcelPoint -- missing Agent Id should return None'
        self.assertIsNone(received, msg)

    def test_process_valid_record_not_parcel_point(self):
        """Process valid record - not parcel point.
        """
        line = self._c.get('test_lines', 'VALID_LINE')
        received = self._f.process(line)
        msg = 'Valid ParcelPoint -- not ParcelPoint should return False'
        self.assertFalse(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._c = None
        del cls._c
        cls._f = None
        del cls._f
