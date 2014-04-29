import unittest2
import os
import datetime
import tempfile

import nparcel
from nparcel.utils.files import (remove_files,
                                 get_directory_files_list)


class TestReporterDaemonNonCompliance(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()
        bu_ids = {1: 'Toll Priority',
                  2: 'Toll Fast',
                  3: 'Toll IPEC'}

        cls._rd = nparcel.ReporterDaemon('noncompliance', pidfile=None)

        cls._rd.emailer.set_template_base(os.path.join('nparcel',
                                                       'templates'))
        cls._rd.set_outfile('Stocktake_noncompliance_')
        cls._dir = tempfile.mkdtemp()
        cls._rd.set_outdir(cls._dir)

        cls._rd.set_recipients(['loumar@tollgroup.com'])

        bu_ids = {1: 'Toll Priority',
                  2: 'Toll Fast',
                  3: 'Toll IPEC'}
        cls._rd.set_bu_ids(bu_ids)
        cls._rd.set_delivery_partners(['Nparcel'])
        kwargs = cls._rd.reporter_kwargs
        cls._rd._report = nparcel.NonCompliance(**kwargs)

        # Prepare some sample data.
        db = cls._rd._report.db
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixtures = [{'db': db.agent_stocktake,
                     'fixture': 'agent_stocktakes.py'},
                    {'db': db.agent,
                     'fixture': 'agents.py'},
                    {'db': db.delivery_partner,
                     'fixture': 'delivery_partners.py'},
                    {'db': db.identity_type,
                     'fixture': 'identity_type.py'},
                    {'db': db.job,
                     'fixture': 'jobs.py'},
                    {'db': db.jobitem,
                     'fixture': 'jobitems.py'}]

        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        # "job" table timestamp updates.
        sql = """UPDATE job
SET job_ts = '%s'""" % cls._now
        db(sql)

        # "job_item" table timestamp updates.
        sql = """UPDATE job_item
SET created_ts = '%s'
WHERE id IN (15, 16, 19, 20, 22)""" % cls._now
        db(sql)

        cls._old_date = cls._now - datetime.timedelta(8)
        cls._older_date = cls._now - datetime.timedelta(10)

        sql = """UPDATE agent_stocktake
SET created_ts = '%s'
WHERE id IN (6)""" % cls._old_date
        db(sql)

        sql = """UPDATE agent_stocktake
SET created_ts = '%s'
WHERE id IN (7, 8)""" % cls._older_date
        db(sql)

        db.commit()

    def test_start(self):
        """ReporterDaemon _start processing loop -- noncompliance.
        """
        dry = True

        old_dry = self._rd.dry

        old_outfile = self._rd.outfile
        self._rd.set_outfile('Stocktake_non-compliance_')

        old_display_hrds = self._rd.display_hdrs
        display_hdrs = ['DP_CODE',
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
        self._rd.set_display_hdrs(display_hdrs)
        old_aliases = self._rd.aliases
        aliases = {'DP_CODE': 'TPP Agent',
                   'AGENT_CODE': 'TPP Agent Id',
                   'AGENT_NAME': 'TPP Agent Name',
                   'ST_DP_CODE': 'Scanning Agent',
                   'ST_AGENT_CODE': 'Scanning Agent Id',
                   'ST_AGENT_NAME': 'Scanning Agent Name',
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
        self._rd.set_aliases(aliases)

        old_widths = self._rd.header_widths
        # Make these lower case to compensate for ConfigParser
        widths = {'tpp agent': 12,
                  'tpp agent id': 12,
                  'tpp agent name': 40,
                  'scanning agent': 14,
                  'scanning agent id': 16,
                  'scanning agent name': 25,
                  'business unit': 20,
                  'agent address': 30,
                  'phone nbr': 15,
                  'connote': 25,
                  'item nbr': 25,
                  'to': 20,
                  'handover': 20}
        self._rd.set_header_widths(widths)

        old_ws = self._rd.ws
        title = 'Toll Parcel Portal Stocktake Non-Compliance Report'
        ws = {'title': title,
              'subtitle': 'ITEMS IN TPP SYSTEM, NOT SCANNED BY AGENT',
              'sheet_title': 'Non-compliance'}
        self._rd.set_ws(ws)

        self._rd.set_dry(dry)
        self._rd._start(self._rd.exit_event)

        # Clean up.
        self._rd.set_dry(old_dry)
        self._rd.set_outfile(old_outfile)
        self._rd.set_display_hdrs(old_display_hrds)
        self._rd.set_aliases(old_aliases)
        self._rd.set_header_widths(old_widths)
        self._rd.set_ws(old_ws)
        self._rd.exit_event.clear()
        remove_files(get_directory_files_list(self._dir))

    def test_send(self):
        """Send the report to the recipients list'
        """
        dry = True

        old_dry = self._rd.dry
        self._rd.set_dry(dry)

        old_report_filename = self._rd.report_filename
        file = 'Stocktake_non-compliance_20140121-13:38-all.xlsx'
        attach_file = os.path.join('nparcel', 'tests', 'files', file)
        self._rd.set_report_filename(attach_file)

        old_ws = self._rd.ws
        title = 'Toll Parcel Portal Stocktake Non-Compliance Report'
        now = self._now.strftime('%d/%m/%Y')
        self._rd.set_ws({'title': title})

        old_recipients = self._rd.recipients
        self._rd.set_recipients(['loumar@tollgroup.com'])

        now = self._now.strftime('%d/%m/%Y %H:%M')
        self._rd.send_email(bu='all', date_ts=self._now)

        # Clean up.
        self._rd.set_dry(old_dry)
        self._rd.set_report_filename(old_report_filename)
        self._rd.set_ws(old_ws)
        self._rd.set_recipients(old_recipients)

    def test_reporter_kwargs(self):
        """Verify the reporter_kwargs for the noncompliance report.
        """
        received = self._rd.reporter_kwargs
        expected = {'bu_ids': {1: 'Toll Priority',
                               2: 'Toll Fast',
                               3: 'Toll IPEC'},
                    'delivery_partners': ['Nparcel']}
        msg = 'reporter_kwargs structure error -- noncompliance'
        self.assertDictEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        del cls._rd
        del cls._now
        os.removedirs(cls._dir)
        del cls._dir
