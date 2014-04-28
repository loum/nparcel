import unittest2
import os

import nparcel


class TestReporterB2CConfig(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._file = os.path.join('nparcel', 'conf', 'top.conf')

    def setUp(self):
        sconfig_file = os.path.join('nparcel', 'conf', 'top.conf')
        self._rc = nparcel.ReporterB2CConfig()

    def test_init(self):
        """Initialise a ReporterB2CConfig object.
        """
        msg = 'Object is not a nparcel.ReporterB2CConfig'
        self.assertIsInstance(self._rc, nparcel.ReporterB2CConfig, msg)

    def test_parse_config(self):
        """Parse comms items from the config.
        """
        config_file = os.path.join('nparcel', 'conf', 'top.conf')
        self._rc.set_config_file(config_file)
        self._rc.parse_config()

        received = self._rc.report_bu_ids
        expected = {1: 'Toll Priority',
                    2: 'Toll Fast',
                    3: 'Toll IPEC'}
        msg = 'report_bu_ids section error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_outdir
        expected = os.path.join(os.sep, 'data', 'nparcel', 'reports')
        msg = 'Config report outdir value error'
        self.assertEqual(received, expected, msg)

        received = self._rc.report_outfile
        expected = 'Report_'
        msg = 'report_base.outfile error'
        self.assertEqual(received, expected, msg)

        received = self._rc.report_outfile_ts_format
        expected = '%Y%m%d-%H:%M'
        msg = 'report_base.outfile_ts_format error'
        self.assertEqual(received, expected, msg)

        received = self._rc.report_extension
        expected = 'xlsx'
        msg = 'report_base.extension error'
        self.assertEqual(received, expected, msg)

    def test_parse_reporter_uncollected(self):
        """Parse items from the config -- reporter uncollected.
        """
        old_report_type = self._rc.report_type
        self._rc.set_report_type('uncollected')
        self._rc.set_config_file(self._file)
        self._rc.parse_config()

        received = self._rc.report_type_outfile
        expected = 'Stocktake_uncollected_aged_report_'
        msg = 'report_uncollected.outfile error'
        self.assertEqual(received, expected, msg)

        received = self._rc.report_type_display_hdrs
        expected = ['DP_CODE',
                    'AGENT_CODE',
                    'AGENT_NAME',
                    'JOB_BU_ID',
                    'AGENT_ADDRESS',
                    'AGENT_SUBURB',
                    'AGENT_POSTCODE',
                    'AGENT_STATE',
                    'AGENT_PHONE_NBR',
                    'CONNOTE_NBR',
                    'ITEM_NBR',
                    'CONSUMER_NAME',
                    'PIECES',
                    'JOB_TS',
                    'DELTA_TIME']
        msg = 'report_uncollected.display_hdrs error'
        self.assertListEqual(received, expected, msg)

        received = self._rc.report_type_aliases
        expected = {'DP_CODE': 'Agent',
                    'AGENT_CODE': 'Agent Id',
                    'AGENT_NAME': 'Agent Name',
                    'JOB_BU_ID': 'Business Unit',
                    'AGENT_ADDRESS': 'Agent Address',
                    'AGENT_SUBURB': 'Suburb',
                    'AGENT_POSTCODE': 'Postcode',
                    'AGENT_STATE': 'State',
                    'AGENT_PHONE_NBR': 'Phone Nbr',
                    'CONNOTE_NBR': 'Connote',
                    'ITEM_NBR': 'Item Nbr',
                    'CONSUMER_NAME': 'To',
                    'PIECES': 'Pieces',
                    'JOB_TS': 'Handover',
                    'DELTA_TIME': 'Days'}
        msg = 'report_uncollected.aliases error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_ws
        title = 'Toll Parcel Portal Stocktake Uncollected (Aged) Report'
        subtitle = 'ITEMS UNCOLLECTED FOR MORE THAN 7 DAYS'
        expected = {'title': title,
                    'subtitle': subtitle,
                    'sheet_title': 'Uncollected'}
        msg = 'report_uncollected_ws error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_delivery_partners
        expected = ['Nparcel']
        msg = 'report_uncollected_delivery_partner error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._rc.set_report_type(old_report_type)

        received = self._rc.report_type_widths
        expected = {'agent name': 20,
                    'agent address': 20,
                    'suburb': 20,
                    'phone nbr': 15,
                    'connote': 25,
                    'item nbr': 25,
                    'to': 20,
                    'handover': 30}
        msg = 'report_uncollected_widths error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_recipients
        expected = []
        msg = 'report_uncollected.recipients error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._rc.report_type_bu_based
        msg = 'report_uncollected.bu_based error'
        self.assertTrue(received, msg)

    def test_parse_reporter_compliance(self):
        """Parse items from the config -- reporter compliance.
        """
        old_report_type = self._rc.report_type
        self._rc.set_report_type('compliance')
        self._rc.set_config_file(self._file)
        self._rc.parse_config()

        received = self._rc.report_type_outfile
        expected = 'Stocktake_compliance_'
        msg = 'report_compliance.outfile error'
        self.assertEqual(received, expected, msg)

        received = self._rc.report_type_display_hdrs
        expected = ['DP_CODE',
                    'AGENT_CODE',
                    'AGENT_NAME',
                    'CREATED_TS']
        msg = 'report_compliance.display_hdrs error'
        self.assertListEqual(received, expected, msg)

        received = self._rc.report_type_aliases
        expected = {'DP_CODE': 'Agent',
                    'AGENT_CODE': 'Agent Id',
                    'AGENT_NAME': 'Agent Name',
                    'CREATED_TS': 'Last completed stocktake'}
        msg = 'report_compliance_aliases section error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_widths
        expected = {'agent name': 40,
                    'last completed stocktake': 30}
        msg = 'report_compliance_widths error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_ws
        title = 'Toll Parcel Portal Stocktake Compliance Report'
        expected = {'title': title,
                    'sheet_title': 'Compliance'}
        msg = 'report_compliance_ws error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_recipients
        expected = []
        msg = 'report_compliance_recipients error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._rc.report_type_bu_based
        msg = 'report_compliance.bu_based error'
        self.assertFalse(received, msg)

        received = self._rc.report_compliance_period
        expected = 7
        msg = 'report_compliance.period error'
        self.assertEqual(received, expected, msg)

        received = self._rc.report_type_delivery_partners
        expected = ['Nparcel']
        msg = 'report_compliance_delivery_partner error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._rc.set_report_type(old_report_type)

    def test_parse_reporter_noncompliance(self):
        """Parse items from the config -- reporter noncompliance.
        """
        old_report_type = self._rc.report_type
        self._rc.set_report_type('noncompliance')
        self._rc.set_config_file(self._file)
        self._rc.parse_config()

        received = self._rc.report_type_outfile
        expected = 'Stocktake_noncompliance_'
        msg = 'report_noncompliance.outfile error'
        self.assertEqual(received, expected, msg)

        received = self._rc.report_type_display_hdrs
        expected = ['DP_CODE',
                    'AGENT_CODE',
                    'AGENT_NAME',
                    'ST_DP_CODE',
                    'ST_AGENT_CODE',
                    'ST_AGENT_NAME',
                    'JOB_BU_ID',
                    'AGENT_ADDRESS',
                    'AGENT_SUBURB',
                    'AGENT_POSTCODE',
                    'AGENT_STATE',
                    'AGENT_PHONE_NBR',
                    'CONNOTE_NBR',
                    'ITEM_NBR',
                    'CONSUMER_NAME',
                    'PIECES',
                    'JOB_TS',
                    'DELTA_TIME']
        msg = 'report_noncompliance.display_hdrs error'
        self.assertListEqual(received, expected, msg)

        received = self._rc.report_type_aliases
        expected = {'DP_CODE': 'Agent',
                    'AGENT_CODE': 'Agent Id',
                    'AGENT_NAME': 'Agent Name',
                    'ST_AGENT_CODE': 'Scanning Agent Id',
                    'ST_AGENT_NAME': 'Scanning Agent Name',
                    'ST_DP_CODE': 'Scanning Agent',
                    'JOB_BU_ID': 'Business Unit',
                    'AGENT_ADDRESS': 'Agent Address',
                    'AGENT_SUBURB': 'Suburb',
                    'AGENT_POSTCODE': 'Postcode',
                    'AGENT_STATE': 'State',
                    'AGENT_PHONE_NBR': 'Phone Nbr',
                    'CONNOTE_NBR': 'Connote',
                    'ITEM_NBR': 'Item Nbr',
                    'CONSUMER_NAME': 'To',
                    'PIECES': 'Pieces',
                    'JOB_TS': 'Handover',
                    'DELTA_TIME': 'Days'}
        msg = 'report_noncompliance_aliases error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_widths
        expected = {'tpp agent': 10,
                    'tpp agent id': 10,
                    'tpp agent name': 40,
                    'scanning agent': 12,
                    'scanning agent id': 14,
                    'scanning agent name': 25,
                    'business unit': 12,
                    'agent address': 30,
                    'suburb': 20,
                    'phone nbr': 15,
                    'connote': 25,
                    'item nbr': 25,
                    'to': 20,
                    'handover': 20}
        msg = 'report_noncompliance_widths error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_ws
        title = 'Toll Parcel Portal Stocktake Non-Compliance Report'
        subtitle = 'ITEMS IN TPP SYSTEM, NOT SCANNED BY AGENT'
        expected = {'title': title,
                    'subtitle': subtitle,
                    'sheet_title': 'Non-Compliance'}
        msg = 'report_noncompliance_ws error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_recipients
        expected = ['loumar@tollgroup.com']
        msg = 'report_noncompliance_recipients error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._rc.report_type_bu_based
        msg = 'report_noncompliance.bu_based error'
        self.assertFalse(received, msg)

        received = self._rc.report_type_delivery_partners
        expected = ['Nparcel']
        msg = 'report_noncompliance_delivery_partner error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._rc.set_report_type(old_report_type)

    def test_parse_reporter_exception(self):
        """Parse items from the config -- reporter exception.
        """
        old_report_type = self._rc.report_type
        self._rc.set_report_type('exception')
        self._rc.set_config_file(self._file)
        self._rc.parse_config()

        received = self._rc.report_type_outfile
        expected = 'Stocktake_exception_'
        msg = 'report_exception.outfile error'
        self.assertEqual(received, expected, msg)

        received = self._rc.report_type_display_hdrs
        expected = ['DP_CODE',
                    'AGENT_CODE',
                    'AGENT_NAME',
                    'REFERENCE_NBR']
        msg = 'report_exception.display_hdrs error'
        self.assertListEqual(received, expected, msg)

        received = self._rc.report_type_aliases
        expected = {'DP_CODE': 'Agent',
                    'AGENT_CODE': 'Agent Id',
                    'AGENT_NAME': 'Agent Name',
                    'REFERENCE_NBR': 'Connote / Item Nbr'}
        msg = 'report_exception_aliases error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_widths
        expected = {'agent': 25,
                    'agent id': 20,
                    'agent name': 40,
                    'connote / item nbr': 40}
        msg = 'report_exception_widths error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_ws
        title = 'Toll Parcel Portal Stocktake Exception Report'
        subtitle = 'ITEMS SCANNED BY AGENT, NOT FOUND IN TPP'
        expected = {'title': title,
                    'subtitle': subtitle,
                    'sheet_title': 'Exception'}
        msg = 'report_exception_ws error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_recipients
        expected = ['loumar@tollgroup.com']
        msg = 'report_exception_recipients error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._rc.report_type_recipients
        expected = ['loumar@tollgroup.com']
        msg = 'report_exception_recipients error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._rc.report_type_bu_based
        msg = 'report_exception.bu_based error'
        self.assertFalse(received, msg)

        received = self._rc.report_type_delivery_partners
        expected = ['Nparcel']
        msg = 'report_exception_delivery_partner error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._rc.set_report_type(old_report_type)

    def test_parse_reporter_totals(self):
        """Parse items from the config -- reporter totals.
        """
        old_report_type = self._rc.report_type
        self._rc.set_report_type('totals')
        self._rc.set_config_file(self._file)
        self._rc.parse_config()

        received = self._rc.report_type_outfile
        expected = 'Stocktake_totals_'
        msg = 'report_totals.outfile error'
        self.assertEqual(received, expected, msg)

        received = self._rc.report_type_display_hdrs
        expected = ['DP_CODE',
                    'AGENT_CODE',
                    'AGENT_NAME',
                    'STOCKTAKE_CREATED_TS',
                    'AGENT_PIECES',
                    'TPP_PIECES']
        msg = 'report_totals.display_hdrs error'
        self.assertListEqual(received, expected, msg)

        received = self._rc.report_type_aliases
        expected = {'DP_CODE': 'Agent',
                    'AGENT_CODE': 'Agent Id',
                    'AGENT_NAME': 'Agent Name',
                    'STOCKTAKE_CREATED_TS': 'Stocktake Date',
                    'AGENT_PIECES': 'Number of parcels scanned',
                    'TPP_PIECES': 'TPP - Number of parcels at agency'}
        msg = 'report_totals_aliases error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_widths
        expected = {'agent name': 30,
                    'number of parcels scanned': 22,
                    'tpp - number of parcels at agency': 27,
                    'stocktake date': 30}
        msg = 'report_totals_widths error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_ws
        title = 'Toll Parcel Portal Stocktake Parcel Totals Report'
        subtitle = ''
        expected = {'title': title,
                    'subtitle': subtitle,
                    'sheet_title': 'Parcel Totals'}
        msg = 'report_totals_ws error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_recipients
        expected = ['loumar@tollgroup.com']
        msg = 'report_totals_recipients value error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._rc.report_type_bu_based
        msg = 'report_totals.bu_based error'
        self.assertFalse(received, msg)

        received = self._rc.report_type_delivery_partners
        expected = ['Nparcel']
        msg = 'report_totals_delivery_partner error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._rc.set_report_type(old_report_type)

    def test_parse_reporter_collected(self):
        """Parse items from the config -- reporter collected.
        """
        old_report_type = self._rc.report_type
        self._rc.set_report_type('collected')
        self._rc.set_config_file(self._file)
        self._rc.parse_config()

        received = self._rc.report_type_display_hdrs
        expected = ['DP_CODE',
                    'AGENT_CODE',
                    'AGENT_NAME',
                    'JOB_BU_ID',
                    'CONNOTE_NBR',
                    'ITEM_NBR',
                    'CONSUMER_NAME',
                    'PIECES',
                    'JOB_TS',
                    'PICKUP_TS',
                    'STOCKTAKE_CREATED_TS']
        msg = 'report_collected.display_hdrs error'
        self.assertListEqual(received, expected, msg)

        received = self._rc.report_type_aliases
        expected = {'DP_CODE': 'Agent',
                    'AGENT_CODE': 'Agent Id',
                    'AGENT_NAME': 'Agent Name',
                    'JOB_BU_ID': 'Business Unit',
                    'CONNOTE_NBR': 'Connote',
                    'ITEM_NBR': 'Item Nbr',
                    'CONSUMER_NAME': 'To',
                    'PIECES': 'Pieces',
                    'JOB_TS': 'Handover',
                    'PICKUP_TS': 'Collected',
                    'STOCKTAKE_CREATED_TS': 'Stocktake Date'}
        msg = 'report_collected_aliases error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_widths
        expected = {'agent name': 30,
                    'business unit': 20,
                    'connote': 25,
                    'item nbr': 25,
                    'to': 20,
                    'handover': 30,
                    'collected': 30,
                    'stocktake date': 30}
        msg = 'report_collected_widths error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_ws
        title = 'Toll Parcel Portal Stocktake Collected Exception Report'
        subtitle = 'ITEMS SCANNED BY AGENT, STATUS IS COLLECTED'
        expected = {'title': title,
                    'subtitle': subtitle,
                    'sheet_title': 'Scanned but collected'}
        msg = 'report_collected_ws error'
        self.assertDictEqual(received, expected, msg)

        received = self._rc.report_type_recipients
        expected = ['loumar@tollgroup.com']
        msg = 'report_collected_recipients error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        received = self._rc.report_type_bu_based
        msg = 'report_collected.bu_based error'
        self.assertFalse(received, msg)

        received = self._rc.report_type_delivery_partners
        expected = ['Nparcel']
        msg = 'report_collected_delivery_partner error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._rc.set_report_type(old_report_type)

    def test_parse_report_bu_id_recipients(self):
        """Parse items from the config -- reporter BU ID recipients.
        """
        self._rc.set_config_file(self._file)
        self._rc.parse_config()

        received = self._rc.report_bu_id_recipients
        expected = {1: ['loumar@tollgroup.com', 'lou.markovski@gmail.com'],
                    2: ['lou.markovski@gmail.com'],
                    3: ['lou@triple20.com.au']}
        msg = 'Config BU ID recipients value error'
        self.assertDictEqual(received, expected, msg)

    def tearDown(self):
        del self._rc

    @classmethod
    def tearDownClass(cls):
        del cls._file
