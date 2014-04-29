import unittest2
import os

import top


class TestFilter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        test_conf = os.path.join('top', 'tests', 'test_loader.conf')
        cls._c = top.Config(config_file=test_conf)
        cls._fltr = top.Filter()

    def test_init(self):
        """Initialise a Filter object.
        """
        msg = 'Object is not an top.Filter'
        self.assertIsInstance(self._fltr, top.Filter, msg)

    def test_process_valid_record_parcel_point(self):
        """Process valid record.
        """
        line = self._c.get('test_lines', 'PP')
        received = self._fltr.process(line, rules=['P', 'R'])
        msg = 'Valid ParcelPoint record should return True'
        self.assertTrue(received, msg)

    def test_process_missing_agent_id(self):
        """Process valid record -- missing Agent Id.
        """
        line = self._c.get('test_lines', 'PP_MISSING_AGENT_ID')
        received = self._fltr.process(line, rules=['P', 'R'])
        msg = 'Valid ParcelPoint -- missing Agent Id should return False'
        self.assertFalse(received, msg)

    def test_process_valid_record_not_parcel_point(self):
        """Process valid record - not parcel point.
        """
        line = self._c.get('test_lines', 'VALID_LINE')
        received = self._fltr.process(line, rules=['P', 'R'])
        msg = 'Valid ParcelPoint -- not ParcelPoint should return None'
        self.assertIsNone(received, msg)

    def test_process_valid_record_r_type_agent_code(self):
        """Process valid record - ParcelPoint R-type agent code.
        """
        line = self._c.get('test_lines', 'PP_R_TYPE_AGENT_CODE')
        received = self._fltr.process(line, rules=['P', 'R'])
        msg = 'Valid ParcelPoint -- ParcelPoint R-type agent code'
        self.assertTrue(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._c = None
        del cls._c
        cls._fltr = None
        del cls._fltr
