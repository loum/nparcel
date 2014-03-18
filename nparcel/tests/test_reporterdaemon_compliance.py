import unittest2
import os
import datetime
import tempfile

import nparcel
from nparcel.utils.files import (remove_files,
                                 get_directory_files_list)


class TestReporterDaemonCompliance(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._ud = nparcel.ReporterDaemon('compliance', pidfile=None)

        cls._ud.emailer.set_template_base(os.path.join('nparcel',
                                                       'templates'))
        cls._ud.set_outfile('Stocktake_compliance_')
        cls._dir = tempfile.mkdtemp()
        cls._ud.set_outdir(cls._dir)

        cls._ud.set_recipients(['loumar@tollgroup.com'])

        bu_ids = {1: 'Toll Priority',
                  2: 'Toll Fast',
                  3: 'Toll IPEC'}
        cls._ud.set_bu_ids(bu_ids)
        cls._ud.set_delivery_partners(['Nparcel'])
        kwargs = cls._ud.reporter_kwargs
        cls._ud._report = nparcel.Compliance(**kwargs)

        # Prepare some sample data.
        db = cls._ud._report.db
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

        old_date = cls._now - datetime.timedelta(8)
        older_date = cls._now - datetime.timedelta(10)

        sql = """UPDATE agent_stocktake
SET created_ts = '%s'
WHERE id IN (6)""" % old_date
        db(sql)

        sql = """UPDATE agent_stocktake
SET created_ts = '%s'
WHERE id IN (7, 8)""" % older_date
        db(sql)

        db.commit()

    def test_start(self):
        """ReporterDaemon _start processing loop -- compliance.
        """
        dry = True

        old_dry = self._ud.dry
        old_display_hrds = self._ud.display_hdrs
        display_hdrs = ['DP_CODE',
                        'AGENT_CODE',
                        'AGENT_NAME',
                        'CREATED_TS']
        self._ud.set_display_hdrs(display_hdrs)
        old_aliases = self._ud.aliases
        aliases = {'DP_CODE': 'Agent',
                   'AGENT_CODE': 'Agent Id',
                   'AGENT_NAME': 'Agent Name',
                   'CREATED_TS': 'Last completed stocktake'}
        self._ud.set_aliases(aliases)

        old_widths = self._ud.header_widths
        # Make these lower case to compensate for ConfigParser
        widths = {'agent name': 40,
                  'last completed stocktake': 30}
        self._ud.set_header_widths(widths)
        old_ws = self._ud.ws
        title = 'Toll Parcel Portal Stocktake Compliance Report'
        ws = {'title': title,
              'sheet_title': 'Compliance'}
        self._ud.set_ws(ws)

        self._ud.set_dry(dry)
        self._ud._start(self._ud.exit_event)

        # Clean up.
        self._ud.set_dry(old_dry)
        self._ud.set_display_hdrs(old_display_hrds)
        self._ud.set_aliases(old_aliases)
        self._ud.set_header_widths(old_widths)
        self._ud.set_ws(old_ws)
        self._ud.exit_event.clear()
        remove_files(get_directory_files_list(self._dir))

    def test_send(self):
        """Send the report to the recipients list'
        """
        dry = True

        old_dry = self._ud.dry
        self._ud.set_dry(dry)

        old_report_filename = self._ud.report_filename
        file = 'Stocktake_compliance_20131211-20:37-all.xlsx'
        attach_file = os.path.join('nparcel', 'tests', 'files', file)
        self._ud.set_report_filename(attach_file)

        old_ws = self._ud.ws
        title = 'Toll Parcel Portal Compliance Report'
        now = self._now.strftime('%d/%m/%Y')
        self._ud.set_ws({'title': title})

        old_recipients = self._ud.recipients
        self._ud.set_recipients(['loumar@tollgroup.com'])

        now = self._now.strftime('%d/%m/%Y %H:%M')
        self._ud.send_email(bu='all', date_ts=self._now)

        # Clean up.
        self._ud.set_dry(old_dry)
        self._ud.set_report_filename(old_report_filename)
        self._ud.set_ws(old_ws)
        self._ud.set_recipients(old_recipients)

    @classmethod
    def tearDownClass(cls):
        cls._ud = None
        del cls._ud
        cls._now = None
        del cls._now
        os.removedirs(cls._dir)
        cls._dir = None
        del cls._dir
