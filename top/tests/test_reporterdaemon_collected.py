import unittest2
import os
import datetime
import tempfile

import top
from top.utils.files import (remove_files,
                             get_directory_files_list)


class TestReporterDaemonCollected(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._rd = top.ReporterDaemon('collected', pidfile=None)

        cls._rd.emailer.set_template_base(os.path.join('top',
                                                       'templates'))
        cls._rd.set_outfile('Stocktake_collected_')
        cls._dir = tempfile.mkdtemp()
        cls._rd.set_outdir(cls._dir)

        cls._rd.set_bu_id_recipients({1: ['loumar@tollgroup.com'],
                                      2: ['lou.markovski@gmail.com'],
                                      3: ['lou@triple20.com.au']})
        cls._rd.set_recipients(['loumar@tollgroup.com'])

        bu_ids = {1: 'Toll Priority',
                  2: 'Toll Fast',
                  3: 'Toll IPEC'}
        cls._rd.set_bu_ids(bu_ids)
        cls._rd.set_delivery_partners(['Nparcel'])
        kwargs = cls._rd.reporter_kwargs
        cls._rd._report = top.Collected(**kwargs)

        # Prepare some sample data.
        db = cls._rd._report.db
        fixture_dir = os.path.join('top', 'tests', 'fixtures')
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
        cls._early_pickup_ts = cls._now - datetime.timedelta(100)
        sql = """UPDATE job_item
 SET created_ts = '%(now)s', pickup_ts = '%(dt)s'
 WHERE id IN (21)""" % {'now': cls._now,
                        'dt': cls._early_pickup_ts}
        db(sql)

        db.commit()

    def test_init(self):
        """Intialise a ReporterDaemon object.
        """
        msg = 'Not a top.ReporterDaemon object'
        self.assertIsInstance(self._rd, top.ReporterDaemon, msg)

    def test_start(self):
        """ReporterDaemon _start processing loop -- collected.
        """
        dry = True

        old_dry = self._rd.dry
        old_display_hrds = self._rd.display_hdrs
        display_hdrs = ['DP_CODE',
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
        self._rd.set_display_hdrs(display_hdrs)
        old_aliases = self._rd.aliases
        aliases = {'DP_CODE': 'Agent',
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
        self._rd.set_aliases(aliases)

        old_widths = self._rd.header_widths
        # Make these lower case to compensate for ConfigParser
        widths = {'agent name': 30,
                  'business unit': 20,
                  'connote': 25,
                  'item nbr': 25,
                  'to': 20,
                  'handover': 30,
                  'collected': 30,
                  'stocktake date': 30}
        self._rd.set_header_widths(widths)

        old_ws = self._rd.ws
        title = 'Toll Outlet Portal Stocktake Collected Exception Report'
        ws = {'title': title,
              'subtitle': 'ITEMS SCANNED BY AGENT, STATUS IS COLLECTED',
              'sheet_title': 'Scanned but collected'}
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
        file = 'Stocktake_collected_20140115-10:20-all.xlsx'
        attach_file = os.path.join('top', 'tests', 'files', file)
        self._rd.set_report_filename(attach_file)

        old_ws = self._rd.ws
        title = 'Toll Outlet Portal Stocktake Collected Exception Report'
        now = self._now.strftime('%d/%m/%Y')
        self._rd.set_ws({'title': title})

        tmp_recipients = self._rd.bu_id_recipients.get(1)
        if tmp_recipients is None:
            tmp_recipients = []
        subject_bu = self._rd.bu_ids.get(1)
        old_recipients = self._rd.recipients
        self._rd.set_recipients(tmp_recipients)
        now = self._now.strftime('%d/%m/%Y %H:%M')
        self._rd.send_email(date_ts=self._now, bu=subject_bu)

        # Clean up.
        self._rd.set_dry(old_dry)
        self._rd.set_report_filename(old_report_filename)
        self._rd.set_ws(old_ws)
        self._rd.set_recipients(old_recipients)

    def test_reporter_kwargs(self):
        """Verify the reporter_kwargs for the collected report.
        """
        received = self._rd.reporter_kwargs
        expected = {'bu_ids': {1: 'Toll Priority',
                               2: 'Toll Fast',
                               3: 'Toll IPEC'},
                    'delivery_partners': ['Nparcel']}
        msg = 'reporter_kwargs structure error -- collected'
        self.assertDictEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._rd = None
        del cls._rd
        cls._now = None
        del cls._now
        os.removedirs(cls._dir)
        cls._dir = None
        del cls._dir
