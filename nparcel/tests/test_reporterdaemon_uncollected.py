import unittest2
import os
import datetime
import tempfile

import nparcel
from nparcel.utils.files import (remove_files,
                                 get_directory_files_list)


class TestReporterDaemonUncollected(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._ud = nparcel.ReporterDaemon('uncollected', pidfile=None)

        cls._ud.emailer.set_template_base(os.path.join('nparcel',
                                                       'templates'))
        cls._dir = tempfile.mkdtemp()
        cls._ud.set_outdir(cls._dir)

        cls._ud.set_bu_id_recipients({1: ['loumar@tollgroup.com'],
                                      2: ['lou.markovski@gmail.com'],
                                      3: ['lou@triple20.com.au']})
        bu_ids = {1: 'Toll Priority',
                  2: 'Toll Fast',
                  3: 'Toll IPEC'}
        cls._ud.set_bu_ids(bu_ids)
        cls._ud.set_delivery_partners(['Nparcel'])
        cls._ud._report = nparcel.Uncollected(**(cls._ud.reporter_kwargs))

        # Prepare some sample data.
        db = cls._ud._report.db
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixtures = [{'db': db.agent_stocktake,
                     'fixture': 'agent_stocktakes.py'},
                    {'db': db.agent,
                     'fixture': 'agents.py'},
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
WHERE id IN (15, 16, 19, 20, 22)""" % (cls._now - datetime.timedelta(10))
        db(sql)

        db.commit()

    def test_init(self):
        """Intialise a ReporterDaemon object.
        """
        msg = 'Not a nparcel.ReporterDaemon object'
        self.assertIsInstance(self._ud, nparcel.ReporterDaemon, msg)

    def test_start(self):
        """ReporterDaemon Uncollected _start processing loop.
        """
        dry = True

        old_dry = self._ud.dry
        old_display_hrds = self._ud.display_hdrs
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
        self._ud.set_display_hdrs(display_hdrs)
        old_aliases = self._ud.aliases
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
        self._ud.set_aliases(aliases)

        old_widths = self._ud.header_widths
        # Make these lower case to compensate for ConfigParser
        widths = {'agent name': 20,
                  'agent address': 20,
                  'phone nbr': 15,
                  'connote': 25,
                  'item nbr': 25,
                  'to': 20,
                  'handover': 30}
        self._ud.set_header_widths(widths)

        old_ws = self._ud.ws
        title = 'Toll Parcel Portal Stocktake Uncollected (Aged) Report'
        ws = {'title': title,
              'subtitle': 'ITEMS UNCOLLECTED FOR MORE THAN 7 DAYS',
              'sheet_title': 'Uncollected'}
        self._ud.set_ws(ws)

        old_bu_id_recipients = self._ud.bu_id_recipients
        bu_id_recipients = {1: ['loumar@tollgroup.com',
                                'lou.markovski@gmail.com'],
                            2: ['loumar@tollgroup.com'],
                            3: ['loumar@tollgroup.com']}
        self._ud.set_bu_id_recipients(bu_id_recipients)

        old_bu_based = self._ud.bu_based
        self._ud.set_bu_based(True)

        self._ud.set_dry(dry)
        self._ud._start(self._ud.exit_event)

        # Clean up.
        self._ud.set_dry(old_dry)
        self._ud.set_display_hdrs(old_display_hrds)
        self._ud.set_aliases(old_aliases)
        self._ud.set_header_widths(old_widths)
        self._ud.set_ws(old_ws)
        self._ud.set_bu_id_recipients(old_bu_id_recipients)
        self._ud.set_bu_based(old_bu_based)
        self._ud.exit_event.clear()
        remove_files(get_directory_files_list(self._dir))

    def test_send(self):
        """Send the report to the recipients list'
        """
        dry = True

        old_dry = self._ud.dry
        self._ud.set_dry(dry)

        old_report_filename = self._ud.report_filename
        file = 'Stocktake_uncollected_aged_report_20131211-20:43-1.xlsx'
        attach_file = os.path.join('nparcel', 'tests', 'files', file)
        self._ud.set_report_filename(attach_file)

        old_ws = self._ud.ws
        title = 'Toll Parcel Portal Stocktake Uncollected (Aged) Report'
        now = self._now.strftime('%d/%m/%Y')
        self._ud.set_ws({'title': title})

        tmp_recipients = self._ud.bu_id_recipients.get(1)
        if tmp_recipients is None:
            tmp_recipients = []
        subject_bu = self._ud.bu_ids.get(1)
        old_recipients = self._ud.recipients
        self._ud.set_recipients(tmp_recipients)
        now = self._now.strftime('%d/%m/%Y %H:%M')
        self._ud.send_email(date_ts=self._now, bu=subject_bu)

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
