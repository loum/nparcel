import unittest2
import os
import datetime
import tempfile

import nparcel
from nparcel.utils.files import (remove_files,
                                 get_directory_files_list)


class TestReporterDaemonTotals(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._rd = nparcel.ReporterDaemon('totals', pidfile=None)

        cls._rd.emailer.set_template_base(os.path.join('nparcel',
                                                       'templates'))
        cls._rd.set_outfile('Stocktake_parcel_totals_')
        cls._dir = tempfile.mkdtemp()
        cls._rd.set_outdir(cls._dir)

        cls._rd.set_recipients(['loumar@tollgroup.com'])

        bu_ids = {1: 'Toll Priority',
                  2: 'Toll Fast',
                  3: 'Toll IPEC'}
        cls._rd.set_bu_ids(bu_ids)
        cls._rd.set_delivery_partners(['Nparcel'])
        kwargs = cls._rd.reporter_kwargs
        cls._rd._report = nparcel.Totals(**kwargs)

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

        db.commit()

    def test_start(self):
        """ReporterDaemon _start processing loop -- totals.
        """
        dry = True

        old_dry = self._rd.dry
        old_display_hrds = self._rd.display_hdrs
        display_hdrs = ['DP_CODE',
                        'AGENT_CODE',
                        'AGENT_NAME',
                        'STOCKTAKE_CREATED_TS',
                        'AGENT_PIECES',
                        'TPP_PIECES']
        self._rd.set_display_hdrs(display_hdrs)
        old_aliases = self._rd.aliases
        aliases = {'DP_CODE': 'Agent',
                   'AGENT_CODE': 'Agent Id',
                   'AGENT_NAME': 'Agent Name',
                   'STOCKTAKE_CREATED_TS': 'Stocktake Date',
                   'AGENT_PIECES': 'Number of parcels scanned',
                   'TPP_PIECES': 'TPP - Number of parcels at agency'}
        self._rd.set_aliases(aliases)

        old_widths = self._rd.header_widths
        # Make these lower case to compensate for ConfigParser
        widths = {'agent name': 20,
                  'tpp - number of parcels at agency': 27,
                  'stocktake date': 30}
        self._rd.set_header_widths(widths)

        old_ws = self._rd.ws
        title = 'Toll Parcel Portal Stocktake - Total Parcels at agent'
        ws = {'title': title,
              'sheet_title': 'Parcel Totals'}
        self._rd.set_ws(ws)

        self._rd.set_dry(dry)
        self._rd._start(self._rd.exit_event)

        # Clean up.
        self._rd.set_dry(old_dry)
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
        file = 'Stocktake_parcel_totals_20131219-09:46-all.xlsx'
        attach_file = os.path.join('nparcel', 'tests', 'files', file)
        self._rd.set_report_filename(attach_file)

        old_ws = self._rd.ws
        title = 'Toll Parcel Portal Stocktake Parcel Totals Report'
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
        """Verify the reporter_kwargs for the totals report.
        """
        received = self._rd.reporter_kwargs
        expected = {'bu_ids': {1: 'Toll Priority',
                               2: 'Toll Fast',
                               3: 'Toll IPEC'},
                    'delivery_partners': ['Nparcel']}
        msg = 'reporter_kwargs structure error -- totals'
        self.assertDictEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        del cls._rd
        del cls._now
        os.removedirs(cls._dir)
        del cls._dir
