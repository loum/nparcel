import unittest2
import datetime
import tempfile
import os

import nparcel
from nparcel.utils.files import remove_files


FILE_BU = {'tolp': '1', 'tolf': '2', 'toli': '3'}
COND_MAP = {'item_number_excp': False}
COND_MAP_COMMS = {'item_number_excp': False,
                  'send_email': True,
                  'send_sms': True}
COND_MAP_IPEC = {'item_number_excp': True}
VALID_LINE_BARCODE = '4156536111'
VALID_LINE_CONNOTE = '218501217863'


class TestLoader(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        test_conf = 'nparcel/tests/test_loader.conf'
        cls._c = nparcel.Config(config_file=test_conf)
        cls._comms_dir = tempfile.mkdtemp()
        cls._ldr = nparcel.Loader(comms_dir=cls._comms_dir)
        cls._job_ts = cls._ldr.db.date_now()

    def test_init(self):
        """Initialise a Loader object.
        """
        msg = 'Object is not an nparcel.Loader'
        self.assertIsInstance(self._ldr, nparcel.Loader, msg)

    def test_parser_integration(self):
        """Parser object integration.
        """
        msg = 'Loader object does not have a valid Parser object'
        self.assertIsInstance(self._ldr.parser, nparcel.Parser, msg)

    def test_valid_barcode_extract(self):
        """Extract valid barcode.
        """
        line = self._c.get('test_lines', 'VALID_LINE')
        result = self._ldr.parser.parse_line(line)
        received = result.get('Bar code')
        expected = VALID_LINE_BARCODE
        msg = 'Loader Bar code parse should return "%s"' % expected
        self.assertEqual(received, expected, msg)

    def test_processor_valid_record_with_comms_with_recipients(self):
        """Process valid raw T1250 line -- with comms and recipients.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        msg = 'Valid T1250 record should process OK'
        line = self._c.get('test_lines', 'VALID_LINE_WITH_RECIPIENTS')
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP_COMMS), msg)

        # With comms enabled, we should have comms flag files.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        sql = """SELECT id
FROM job_item"""
        self._ldr.db(sql)
        expected = []
        for row in self._ldr.db.rows():
            expected.append(os.path.join(self._comms_dir, '%s.%d.%s') %
                            ('email', row[0], 'body'))
            expected.append(os.path.join(self._comms_dir, '%s.%d.%s') %
                            ('sms', row[0], 'body'))
        msg = 'Comms directory file list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Restore DB state and clean.
        remove_files(received)
        self._ldr.db.rollback()

    def test_processor_valid_record_with_comms_pe_record(self):
        """Process valid raw T1250 line -- with comms for primary elect.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        msg = 'Valid T1250 record should process OK'
        line = self._c.get('test_lines', 'VALID_LINE_PE')
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP_COMMS), msg)

        # With comms enabled and PE, we should NOT have comms flag files.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        expected = []
        msg = 'Comms directory for PE record file list error'
        self.assertListEqual(received, expected, msg)

        # Restore DB state and clean.
        self._ldr.db.rollback()

    def test_processor_valid_record_parcel_point_record(self):
        """Process valid raw T1250 line -- with ParcelPoint Agent code.
        """
        msg = 'Valid ParcelPoint T1250 record should return None'
        line = self._c.get('test_lines', 'PP')
        self.assertIsNone(self._ldr.process(self._job_ts,
                                            line,
                                            FILE_BU.get('tolp'),
                                            COND_MAP_COMMS), msg)

    def test_processor_valid_record_with_comms_no_recipients(self):
        """Process valid raw T1250 line -- with comms no recipients.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        msg = 'Valid T1250 record should process OK'
        line = self._c.get('test_lines', 'VALID_LINE')
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP_COMMS), msg)

        # With comms enabled and no recipients, we should NOT have comms
        # flag files.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        expected = []
        msg = 'Comms directory -- no recipients record file list error'
        self.assertListEqual(received, expected, msg)

        # Restore DB state and clean.
        self._ldr.db.rollback()

    def test_processor_valid_record_no_comms(self):
        """Process valid raw T1250 line -- no comms.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        line = self._c.get('test_lines', 'VALID_LINE')
        msg = 'Valid T1250 record should process OK'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP), msg)

        # With comms disabled, we should have comms flag files.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        expected = []
        msg = 'Comms directory file list error -- valid no comms'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_processor_valid_record_item_number(self):
        """Process valid raw T1250 line -- item number, no exception.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        line = self._c.get('test_lines', 'VALID_ITEM_NUMBER')
        msg = 'Valid T1250 record should process OK'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('toli'),
                                          COND_MAP_IPEC), msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_processor_valid_primary_elect(self):
        """Process valid raw T1250 line -- primary elect.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        line = self._c.get('test_lines', 'PE')
        msg = 'Valid T1250 record should process OK'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('toli'),
                                          COND_MAP_IPEC), msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_table_column_map_for_primary_elect(self):
        """Primary elect valid raw T1250 line and map job table elements.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        line = self._c.get('test_lines', 'PE')
        fields = self._ldr.parser.parse_line(line)
        fields['job_ts'] = self._job_ts
        fields['bu_id'] = int(FILE_BU.get('tolp'))
        received = self._ldr.table_column_map(fields,
                                              nparcel.loader.JOB_MAP,
                                              COND_MAP)
        expected = {'address_1': '31 Bridge st,',
                    'address_2': 'Lane Cove,',
                    'agent_id': 1,
                    'bu_id': 1,
                    'card_ref_nbr': '4156536111',
                    'job_ts': self._job_ts,
                    'postcode': '2066',
                    'service_code': 3,
                    'state': 'NSW',
                    'status': 1,
                    'suburb': 'Australia Other'}
        msg = 'Valid record Job table translation error'
        self.assertDictEqual(received, expected, msg)

    def test_processor_invalid_record_item_number(self):
        """Process valid raw T1250 line -- no item number, exception.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        line = self._c.get('test_lines', 'VALID_LINE')
        msg = 'T1250 record with missing Item Number should return False'
        self.assertFalse(self._ldr.process(self._job_ts,
                                           line,
                                           FILE_BU.get('toli'),
                                           COND_MAP_IPEC), msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_processor_valid_record_single_quote(self):
        """Process valid raw T1250 line.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'V098'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        line = self._c.get('test_lines', 'SINGLE_QUOTE_LINE')
        msg = 'Valid T1250 record should process OK -- single quote'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP), msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_processor_valid_record_dodgy_postcode(self):
        """Process valid raw T1250 line -- dodgy postcode.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'Q067'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        line = self._c.get('test_lines', 'DODGY_POSTCODE')
        msg = 'Valid T1250 record should process OK -- bad postcode'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP), msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_processor_valid_record_update(self):
        """Process valid raw T1250 line with a "job" item Agent Id update.
        """
        # Seed the Agent Ids.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))
        agent_fields = {'code': 'N014'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        line = self._c.get('test_lines', 'VALID_LINE')
        msg = 'Valid T1250 record should process successfully'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP), msg)
        line = self._c.get('test_lines', 'VALID_LINE_AGENT_UPD')
        msg = 'Valid T1250 record update should process successfully'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP), msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_processor_invalid_postcode_record(self):
        """Process valid raw T1250 line -- missing Postcode.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        line = self._c.get('test_lines', 'INVALID_POSTCODE_LINE')
        msg = 'T1250 record should process successfully -- missing postcode'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP), msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_processor_missing_agent_id_record(self):
        """Process valid raw T1250 line -- missing Agent Id.
        """
        line = self._c.get('test_lines', 'VALID_LINE')
        msg = 'Missing Agent Id should fail processing'
        self.assertFalse(self._ldr.process(self._job_ts,
                                           line,
                                           FILE_BU.get('tolp'),
                                           COND_MAP), msg)

    def test_processor_valid_record_existing_barcode(self):
        """Process valid raw T1250 line -- existing barcode.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        # First, create a record and attempt to reload as a duplicate.
        # Should update the Agent Id but not create a new job_item record.
        line = self._c.get('test_lines', 'VALID_LINE')
        msg = 'New T1250 record should process successfully'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP), msg)
        msg = 'Duplicate T1250 record should process successfully'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP), msg)

        sql = self._ldr.db.jobitem.connote_sql(VALID_LINE_CONNOTE)
        self._ldr.db(sql)
        received = []
        for row in self._ldr.db.rows():
            received.append(row[0])
        expected = 1
        msg = 'Connote update should not create additional job_item'
        self.assertEqual(len(received), expected, msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_processor_invalid_barcode_record(self):
        """Process valid raw T1250 line with an invalid barcode.
        """
        line = self._c.get('test_lines', 'INVALID_BARCODE_LINE')
        msg = 'Invalid barcode processing should return False'
        self.assertFalse(self._ldr.process(self._job_ts,
                                           line,
                                           FILE_BU.get('tolp'),
                                           COND_MAP), msg)

    def test_processor_invalid_agent_id_record(self):
        """Process valid raw T1250 line with an invalid barcode.
        """
        msg = 'Invalid Agent Id processing should return False'
        line = self._c.get('test_lines', 'INVALID_AGENTID_LINE')
        self.assertFalse(self._ldr.process(self._job_ts,
                                           line,
                                           FILE_BU.get('tolp'),
                                           COND_MAP), msg)

    def test_processor_manufactured_connote(self):
        """Process valid raw T1250 line with manufactured barcode.
        """
        # Seed the Agent Id.
        agent_fields = [{'code': 'N031'},
                        {'code': 'N032'}]
        for agent_field in agent_fields:
            self._ldr.db(self._ldr.db._agent.insert_sql(agent_field))

        # First, create a manufactured barcode value.
        line = self._c.get('test_lines', 'MANUFACTURED_BC_LINE')
        msg = 'Manufactured barcode creation failed -- no barcode'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP), msg)
        # Now the manufactured barcode value update.
        msg = 'Manufactured barcode creation failed -- existing barcode'
        line = self._c.get('test_lines', 'MANUFACTURED_BC_UPD_LINE')
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP), msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_table_column_map(self):
        """Map parser fields to table columns.
        """
        fields = {'Field 1': 'field 1 value',
                  'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Field 2': {
                   'column': 'field_2',
                   'required': True}}
        received = self._ldr.table_column_map(fields, map, COND_MAP)
        expected = {'field_1': 'field 1 value',
                    'field_2': 'field 2 value'}
        msg = 'Table to column map incorrect'
        self.assertDictEqual(received, expected, msg)

    def test_set_callbacks(self):
        """Set table columns from a callback.
        """

        def test_callback(value):
            return 'new value'

        fields = {'Field 1': 'field 1 value',
                  'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Field 2': {
                   'column': 'field_2',
                   'callback': test_callback,
                   'required': True}}

        self._ldr.set_callbacks(fields, map)
        received = fields
        expected = {'Field 1': 'field 1 value',
                    'Field 2': 'new value'}
        msg = 'Raw fields to table column callback incorrect'
        self.assertDictEqual(received, expected, msg)

    def test_set_defaults_value_already_provided(self):
        """Set table columns from defaults if value provided.
        """
        fields = {'Field 1': 'field 1 value',
                  'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Field 2': {
                   'column': 'field_2',
                   'default': 'banana',
                   'required': True}}

        self._ldr.set_defaults(fields, map)
        received = fields
        expected = {'Field 1': 'field 1 value',
                    'Field 2': 'field 2 value'}
        msg = 'Raw fields to table column default incorrect -- has value'
        self.assertDictEqual(received, expected, msg)

    def test_set_defaults_value_not_provided(self):
        """Set table columns from defaults if value not provided.
        """
        fields = {'Field 1': 'field 1 value',
                  'Field 2': ''}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Field 2': {
                   'column': 'field_2',
                   'default': 'banana',
                   'required': True}}

        self._ldr.set_defaults(fields, map)
        received = fields
        expected = {'Field 1': 'field 1 value',
                    'Field 2': 'banana'}
        msg = 'Raw fields to table column default incorrect -- no value'
        self.assertDictEqual(received, expected, msg)

    def test_set_default_equals_value_already_provided(self):
        """Set table columns from default equals if value provided.
        """
        fields = {'Field 1': 'field 1 value',
                  'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Field 2': {
                   'column': 'field_2',
                   'default_equal': 'Field 1',
                   'required': True}}

        self._ldr.set_default_equals(fields, map, False)
        received = fields
        expected = {'Field 1': 'field 1 value',
                    'Field 2': 'field 2 value'}
        msg = 'Default equals incorrect -- has value'
        self.assertDictEqual(received, expected, msg)

    def test_set_default_equals_value_not_provided(self):
        """Set table columns from default equals if value not provided.
        """
        fields = {'Field 1': 'field 1 value',
                  'Field 2': ''}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Field 2': {
                   'column': 'field_2',
                   'default_equal': 'Field 1',
                   'required': True}}

        self._ldr.set_default_equals(fields, map, False)
        received = fields
        expected = {'Field 1': 'field 1 value',
                    'Field 2': 'field 1 value'}
        msg = 'Default equals incorrect -- no value'
        self.assertDictEqual(received, expected, msg)

    def test_set_default_equals_missing_item_number_raise_excp(self):
        """Default equals if value not provided raises exception.
        """
        fields = {'Field 1': 'field 1 value',
                  'Item Number': ''}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Item Number': {
                   'column': 'field_2',
                   'default_equal': 'Field 1',
                   'required': True}}

        self._ldr.set_default_equals(fields, map, True)
        received = fields
        expected = {'Field 1': 'field 1 value',
                    'Item Number': ''}
        msg = 'Default equals incorrect -- Item Number raises exception'
        self.assertDictEqual(received, expected, msg)

    def test_set_default_equals_missing_item_number_no_excp(self):
        """Default equals if value not provided does not raise exception.
        """
        fields = {'Field 1': 'field 1 value',
                  'Item Number': ''}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Item Number': {
                   'column': 'field_2',
                   'default_equal': 'Field 1',
                   'required': True}}

        self._ldr.set_default_equals(fields, map, False)
        received = fields
        expected = {'Field 1': 'field 1 value',
                    'Item Number': 'field 1 value'}
        msg = 'Default equals incorrect -- Item Number no exception'
        self.assertDictEqual(received, expected, msg)

    def test_set_columns(self):
        """Set table columns from the parsed fields.
        """
        fields = {'Field 1': 'field 1 value',
                  'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Field 2': {
                   'column': 'field_2',
                   'required': True}}
        received = self._ldr.set_columns(fields, map)
        expected = {'field_1': 'field 1 value',
                    'field_2': 'field 2 value'}
        msg = 'Raw fields to table column map incorrect'
        self.assertDictEqual(received, expected, msg)

    def test_table_column_map_missing_required_field_exception(self):
        """Table column map missing required field exception -- no default.
        """
        fields = {'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True},
               'Field 2': {
                   'value': 'field_2',
                   'required': False}}
        self.assertRaisesRegexp(ValueError,
                                'Field "Field 1" is required',
                                self._ldr.table_column_map,
                                fields, map, COND_MAP)

    def test_table_column_map_missing_required_field_with_default(self):
        """Table column map missing required field value with default.
        """
        fields = {'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True,
                   'default': 'field_1_default'},
               'Field 2': {
                   'column': 'field_2',
                   'required': False}}
        received = self._ldr.table_column_map(fields, map, COND_MAP)
        expected = {'field_1': 'field_1_default',
                    'field_2': 'field 2 value'}
        msg = 'Table to column map with missing required field error'
        self.assertDictEqual(received, expected, msg)

    def test_table_column_map_missing_required_field_with_default_eq(self):
        """Table column map missing required field value with default_equal.
        """
        fields = {'Field 2': 'field 2 value'}
        map = {'Field 1': {
                   'column': 'field_1',
                   'required': True,
                   'default_equal': 'Field 2'},
               'Field 2': {
                   'column': 'field_2',
                   'required': False}}
        received = self._ldr.table_column_map(fields, map, COND_MAP)
        expected = {'field_1': 'field 2 value',
                    'field_2': 'field 2 value'}
        msg = 'Table to column map with missing required field error'
        self.assertDictEqual(received, expected, msg)

    def test_table_column_map_for_a_valid_raw_record(self):
        """Process valid raw T1250 line and map job table elements.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        line = self._c.get('test_lines', 'VALID_LINE')
        fields = self._ldr.parser.parse_line(line)
        fields['job_ts'] = self._job_ts
        fields['bu_id'] = int(FILE_BU.get('tolp'))
        received = self._ldr.table_column_map(fields,
                                              nparcel.loader.JOB_MAP,
                                              COND_MAP)
        expected = {'address_1': '31 Bridge st,',
                    'address_2': 'Lane Cove,',
                    'agent_id': 1,
                    'bu_id': 1,
                    'card_ref_nbr': '4156536111',
                    'job_ts': self._job_ts,
                    'postcode': '2066',
                    'service_code': 'NULL',
                    'state': 'NSW',
                    'status': 1,
                    'suburb': 'Australia Other'}
        msg = 'Valid record Job table translation error'
        self.assertDictEqual(received, expected, msg)

    def test_valid_translate_postcode_non_integer(self):
        """Translate postcode to state -- valid, range-based.
        """
        postcode = 'xxx'
        received = self._ldr.translate_postcode(postcode)
        expected = ''
        msg = 'Non-integer postcode translation to state failed'
        self.assertEqual(received, expected, msg)

    def test_valid_translate_postcode_range_based(self):
        """Translate postcode to state -- valid, range-based.
        """
        postcode = 2000
        received = self._ldr.translate_postcode(postcode)
        expected = 'NSW'
        msg = 'Valid postcode (NSW) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 4123
        received = self._ldr.translate_postcode(postcode)
        expected = 'QLD'
        msg = 'Valid postcode (QLD) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 9123
        received = self._ldr.translate_postcode(postcode)
        expected = 'QLD'
        msg = 'Valid postcode (QLD) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 5023
        received = self._ldr.translate_postcode(postcode)
        expected = 'SA'
        msg = 'Valid postcode (SA) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 5855
        received = self._ldr.translate_postcode(postcode)
        expected = 'SA'
        msg = 'Valid postcode (SA) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 6125
        received = self._ldr.translate_postcode(postcode)
        expected = 'WA'
        msg = 'Valid postcode (WA) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 7100
        received = self._ldr.translate_postcode(postcode)
        expected = 'TAS'
        msg = 'Valid postcode (TAS) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 900
        received = self._ldr.translate_postcode(postcode)
        expected = 'NT'
        msg = 'Valid postcode (NT) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

    def test_invalid_translate_postcode_range_based(self):
        """Translate postcode to state -- invalid, range-based.
        """
        postcode = -1
        received = self._ldr.translate_postcode(postcode)
        expected = ''
        msg = 'Invalid postcode translation to state failed -- invalid'
        self.assertEqual(received, expected, msg)

    def test_valid_translate_postcode_exception_based(self):
        """Translate postcode to state -- valid, exception-based.
        """
        postcode = 2899
        received = self._ldr.translate_postcode(postcode)
        expected = 'NSW'
        msg = 'Valid postcode translation to state failed -- exceptions'
        self.assertEqual(received, expected, msg)

    def test_translate_service_code(self):
        """Translate service code.
        """
        sc = '3'
        received = self._ldr.translate_service_code(sc)
        expected = 3
        msg = 'Service Code translation failed'
        self.assertEqual(received, expected, msg)

    def test_translate_service_code_invalid(self):
        """Translate service code -- invalid scenarios.
        """
        expected = 'NULL'
        sc = ''
        received = self._ldr.translate_service_code(sc)
        msg = 'Service Code ("") translation failed'
        #self.assertIsNone(received, msg)
        self.assertEqual(received, expected, msg)

        sc = None
        received = self._ldr.translate_service_code(sc)
        msg = 'Service Code (None) translation failed'
        #self.assertIsNone(received, msg)
        self.assertEqual(received, expected, msg)

    def test_jobitem_table_column_map_for_a_valid_raw_record(self):
        """Process valid raw T1250 line and map "jobitem" table elements.
        """
        line = self._c.get('test_lines', 'VALID_LINE')
        fields = self._ldr.parser.parse_line(line)
        received = self._ldr.table_column_map(fields,
                                              nparcel.loader.JOB_ITEM_MAP,
                                              COND_MAP)
        # Null out the time created.
        received['created_ts'] = None
        expected = {'connote_nbr': '218501217863',
                    'item_nbr': '218501217863',
                    'consumer_name': 'Diane Donohoe',
                    'email_addr': '',
                    'phone_nbr': '',
                    'pieces': '00001',
                    'status': 1,
                    'created_ts': None}
        msg = 'Valid record "jobitem" table translation error'
        self.assertDictEqual(received, expected, msg)

    def test_barcode_exists_with_missing_barcode(self):
        """Check barcode status -- missing barcode.
        """
        msg = 'Missing barcode should return False'
        self.assertFalse(self._ldr.barcode_exists('xxx'), msg)

    def test_barcode_exists_with_existing_barcode(self):
        """Check barcode status -- existing barcode.
        """
        # Seed the barcode.
        barcode_fields = {'card_ref_nbr': VALID_LINE_BARCODE,
                          'job_ts': self._job_ts}
        self._ldr.db(self._ldr.db._job.insert_sql(barcode_fields))

        msg = 'Existing barcode should return True'
        self.assertTrue(self._ldr.barcode_exists(VALID_LINE_BARCODE), msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_agent_id_with_missing_agent_id(self):
        """Agent ID check with missing Agent ID.
        """
        msg = 'Missing Agent ID should return None'
        self.assertIsNone(self._ldr.get_agent_id('xxx'), msg)

    def test_agent_id_existing_agent_id(self):
        """Valid agent ID check.
        """
        # Seed the Agent Id.
        test_agent_id = 'N014'
        agent_fields = {'code': test_agent_id}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        msg = 'Existing barcode should not return None'
        received = self._ldr.get_agent_id(test_agent_id)
        expected = 1
        self.assertEqual(received, expected, msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_match_connote_scenario_connote_lt_15_char(self):
        """Manufactured connote check -- connote < 15 chars.
        """
        msg = 'Connote length < 15 chars scenario check should return False'
        barcode = '41566627'
        connote = '218701663454'
        received = self._ldr.match_connote(connote, barcode)
        self.assertFalse(received, msg)

    def test_match_connote_scenario_connote_gt_15_char_unique_barcode(self):
        """Manufactured connote check -- unique barcode, connote > 15 chars.
        """
        msg = 'Connote length > 15 chars scenario check should return False'
        barcode = '41566627'
        connote = '3142357006912345'
        received = self._ldr.match_connote(connote, barcode)
        self.assertFalse(received, msg)

    def test_match_connote_scenario_connote_gt_15_char_dodgy_barcode(self):
        """Manufactured connote check -- dodgy barcode, connote > 15 chars.
        """
        msg = 'Connote length > 15 chars scenario check should return False'
        barcode = '000931423570069'
        connote = '3142357006912345'
        received = self._ldr.match_connote(connote, barcode)
        self.assertTrue(received, msg)

    def test_match_connote_scenario_connote_gt_15_char_like_start(self):
        """Manufactured connote check -- like start, connote > 15 chars.
        """
        msg = 'Connote length > 15 chars scenario check should return False'
        barcode = '000931423750069'
        connote = '00093142375006909983'
        received = self._ldr.match_connote(connote, barcode)
        self.assertTrue(received, msg)

    def test_get_jobitem_based_job_id(self):
        """Get jobitem-based job id.
        """
        older_ts = datetime.datetime.now() - datetime.timedelta(seconds=999)
        kwargs = {'address_1': '31 Bridge st,',
                  'address_2': 'Lane Cove,',
                  'agent_id': 'N031',
                  'bu_id': 1,
                  'card_ref_nbr': '4156536111',
                  'job_ts': '%s' % older_ts,
                  'status': 1,
                  'suburb': 'Australia Other'}
        sql = self._ldr.db.job.insert_sql(kwargs)
        job_id_old = self._ldr.db.insert(sql)

        kwargs = {'address_1': '31 Bridge st,',
                  'address_2': 'Lane Cove,',
                  'agent_id': 'N031',
                  'bu_id': 1,
                  'card_ref_nbr': '4156536111',
                  'job_ts': self._job_ts,
                  'status': 1,
                  'suburb': 'Australia Other'}
        sql = self._ldr.db.job.insert_sql(kwargs)
        job_id = self._ldr.db.insert(sql)

        kwargs = {'address_1': '32 Banana st,',
                  'address_2': 'Banana Cove,',
                  'agent_id': 'N031',
                  'bu_id': 1,
                  'card_ref_nbr': '4156536112',
                  'job_ts': self._job_ts,
                  'status': 1,
                  'suburb': 'Australia Other'}
        sql = self._ldr.db.job.insert_sql(kwargs)
        dodgy_job_id = self._ldr.db.insert(sql)

        # "job_items" table.
        jobitems = [{'connote_nbr': '218501217863',
                     'item_nbr': 'abcdef00001',
                     'job_id': job_id,
                     'pickup_ts': self._job_ts,
                     'pod_name': 'pod_name 218501217863'},
                    {'connote_nbr': '218501217863',
                     'item_nbr': 'abcdef00002',
                     'job_id': job_id_old,
                     'pickup_ts': self._job_ts,
                     'pod_name': 'pod_name 218501217863'},
                    {'connote_nbr': '111111111111',
                     'item_nbr': 'abcdef00003',
                     'job_id': dodgy_job_id,
                     'pickup_ts': self._job_ts,
                     'pod_name': 'pod_name 111111111111'}]
        for jobitem in jobitems:
            sql = self._ldr.db.jobitem.insert_sql(jobitem)
            self._ldr.db(sql=sql)

        kwargs = {'item_nbr': 'abcdef00001',
                  'connote': '218501217863'}
        received = self._ldr.get_jobitem_based_job_id(**kwargs)
        msg = 'jobitem table based job id query results not as expected'
        self.assertEqual(received, job_id, msg)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_processor_valid_record_revalidate_postcode(self):
        """Process valid raw T1250 line -- no comms.
        """
        # Seed the Agent Id.
        agent_fields = {'code': 'N031'}
        self._ldr.db(self._ldr.db._agent.insert_sql(agent_fields))

        line = self._c.get('test_lines', 'VALID_LINE')
        msg = 'Valid T1250 record should process OK'
        self.assertTrue(self._ldr.process(self._job_ts,
                                          line,
                                          FILE_BU.get('tolp'),
                                          COND_MAP), msg)

        # Overwrite the state.
        sql = """UPDATE job
SET state = 'VIC'"""
        self._ldr.db(sql)

        self._ldr.verify_postcodes(dry=True)

        # Restore DB state.
        self._ldr.db.rollback()

    def test_ignore_record(self):
        """Ignore T1250 record.
        """
        line = self._c.get('test_lines', 'PP')
        fields = self._ldr.parser.parse_line(line)
        received = self._ldr.ignore_record(fields)
        msg = 'Agent code should set ignored flag'
        self.assertTrue(received, msg)

    def test_ignore_record_valid_agent_code(self):
        """Do not ignore T1250 record.
        """
        line = self._c.get('test_lines', 'VALID_LINE')
        fields = self._ldr.parser.parse_line(line)
        received = self._ldr.ignore_record(fields)
        msg = 'Agent code should not set ignored flag'
        self.assertFalse(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._c = None
        del cls._c
        cls._ldr = None
        del cls._ldr
        del cls._job_ts
        os.removedirs(cls._comms_dir)
        del cls._comms_dir
