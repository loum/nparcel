import unittest2
import os
import datetime
import tempfile

import top
from top.utils.files import (remove_files,
                                 get_directory_files_list)


class TestReporterDaemonUncollected(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._rd = top.ReporterDaemon('uncollected', pidfile=None)

        cls._rd.emailer.set_template_base(os.path.join('top',
                                                       'templates'))
        cls._dir = tempfile.mkdtemp()
        cls._rd.set_outdir(cls._dir)

        cls._rd.set_bu_id_recipients({1: ['loumar@tollgroup.com'],
                                      2: ['lou.markovski@gmail.com'],
                                      3: ['lou@triple20.com.au']})
        bu_ids = {1: 'Toll Priority',
                  2: 'Toll Fast',
                  3: 'Toll IPEC'}
        cls._rd.set_bu_ids(bu_ids)
        cls._rd.set_delivery_partners(['Nparcel'])
        cls._rd._report = top.Uncollected(**(cls._rd.reporter_kwargs))

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

        sql = """UPDATE job
SET job_ts = '%s'
WHERE id IN (6, 7, 8)""" % (cls._now - datetime.timedelta(10))
        db(sql)

        # "job_item" table timestamp updates.
        sql = """UPDATE job_item
SET created_ts = '%s'
WHERE id IN (15, 16, 19, 20, 22)""" % (cls._now - datetime.timedelta(10))
        db(sql)

        db.commit()

    def test_init(self):
        """Intialise a ReporterDaemon object.
        """
        msg = 'Not a top.ReporterDaemon object'
        self.assertIsInstance(self._rd, top.ReporterDaemon, msg)

    def test_start(self):
        """ReporterDaemon Uncollected _start processing loop.
        """
        dry = True

        old_dry = self._rd.dry
        old_display_hrds = self._rd.display_hdrs
        display_hdrs = ['DP_CODE',
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
        self._rd.set_display_hdrs(display_hdrs)
        old_aliases = self._rd.aliases
        aliases = {'DP_CODE': 'Agent',
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
        self._rd.set_aliases(aliases)

        old_widths = self._rd.header_widths
        # Make these lower case to compensate for ConfigParser
        widths = {'agent name': 20,
                  'agent address': 20,
                  'phone nbr': 15,
                  'connote': 25,
                  'item nbr': 25,
                  'to': 20,
                  'handover': 30}
        self._rd.set_header_widths(widths)

        old_ws = self._rd.ws
        title = 'Toll Outlet Portal Stocktake Uncollected (Aged) Report'
        ws = {'title': title,
              'subtitle': 'ITEMS UNCOLLECTED FOR MORE THAN 7 DAYS',
              'sheet_title': 'Uncollected'}
        self._rd.set_ws(ws)

        old_bu_id_recipients = self._rd.bu_id_recipients
        bu_id_recipients = {1: ['loumar@tollgroup.com',
                                'lou.markovski@gmail.com'],
                            2: ['loumar@tollgroup.com'],
                            3: ['loumar@tollgroup.com']}
        self._rd.set_bu_id_recipients(bu_id_recipients)

        old_bu_based = self._rd.bu_based
        self._rd.set_bu_based(True)

        self._rd.set_dry(dry)
        self._rd._start(self._rd.exit_event)

        # Clean up.
        self._rd.set_dry(old_dry)
        self._rd.set_display_hdrs(old_display_hrds)
        self._rd.set_aliases(old_aliases)
        self._rd.set_header_widths(old_widths)
        self._rd.set_ws(old_ws)
        self._rd.set_bu_id_recipients(old_bu_id_recipients)
        self._rd.set_bu_based(old_bu_based)
        self._rd.exit_event.clear()
        remove_files(get_directory_files_list(self._dir))

    def test_send(self):
        """Send the report to the recipients list'
        """
        dry = True

        old_dry = self._rd.dry
        self._rd.set_dry(dry)

        old_report_filename = self._rd.report_filename
        file = 'Stocktake_uncollected_aged_report_20131211-20:43-1.xlsx'
        attach_file = os.path.join('top', 'tests', 'files', file)
        self._rd.set_report_filename(attach_file)

        old_ws = self._rd.ws
        title = 'Toll Outlet Portal Stocktake Uncollected (Aged) Report'
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
        """Verify the reporter_kwargs for the uncollected report.
        """
        received = self._rd.reporter_kwargs
        expected = {'bu_ids': {1: 'Toll Priority',
                               2: 'Toll Fast',
                               3: 'Toll IPEC'},
                    'delivery_partners': ['Nparcel']}
        msg = 'reporter_kwargs structure error -- uncollected'
        self.assertDictEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        del cls._rd
        del cls._now
        os.removedirs(cls._dir)
        del cls._dir
