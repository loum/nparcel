import unittest2
import os
import datetime
import tempfile

import nparcel
from nparcel.utils.files import (remove_files,
                                 get_directory_files_list)


class TestReporterDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls._ud = nparcel.ReporterDaemon('uncollected',
                                         pidfile=None)
        db = cls._ud._report.db
        cls._ud.emailer.set_template_base(os.path.join('nparcel',
                                                       'templates'))

        cls._dir = tempfile.mkdtemp()
        cls._ud.set_outdir(cls._dir)

        # Prepare some sample data.
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
WHERE id IN (15, 16, 19, 20, 22)""" % cls._now
        db(sql)

        db.commit()

    def test_init(self):
        """Intialise a ReporterDaemon object.
        """
        msg = 'Not a nparcel.ReporterDaemon object'
        self.assertIsInstance(self._ud, nparcel.ReporterDaemon, msg)

    def test_start(self):
        """ReporterDaemon _start processing loop.
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
        widths = {'Agent Name': 20,
                  'Agent Address': 20,
                  'Phone Nbr': 15,
                  'Connote': 25,
                  'Item Nbr': 25,
                  'To': 20,
                  'Handover': 30}
        self._ud.set_header_widths(widths)
        old_ws = self._ud.ws
        title = 'Toll Parcel Portal Stocktake Uncollected (Aged) Report'
        ws = {'title': title,
              'subtitle': 'ITEMS UNCOLLECTED FOR MORE THAN 7 DAYS',
              'sheet_title': 'Uncollected'}
        self._ud.set_ws(ws)

        old_recipients = self._ud.recipients
        self._ud.set_recipients(['loumar@tollgroup.com'])

        old_bu_id_recipients = self._ud.bu_id_recipients
        bu_id_recipients = {1: ['loumar@tollgroup.com',
                                'lou.markovski@gmail.com'],
                            2: ['loumar@tollgroup.com'],
                            3: ['loumar@tollgroup.com']}
        self._ud.set_bu_id_recipients(bu_id_recipients)

        self._ud.set_dry(dry)
        self._ud._start(self._ud.exit_event)

        # Clean up.
        self._ud.set_dry(old_dry)
        self._ud.set_display_hdrs(old_display_hrds)
        self._ud.set_aliases(old_aliases)
        self._ud.set_header_widths(old_widths)
        self._ud.set_ws(old_ws)
        self._ud.set_recipients(old_recipients)
        self._ud.set_bu_id_recipients(old_bu_id_recipients)
        self._ud.exit_event.clear()
        remove_files(get_directory_files_list(self._dir))

    def test_send(self):
        """Send the report to the recipients list'
        """
        dry = True

        old_dry = self._ud.dry
        self._ud.set_dry(dry)

        old_report_filename = self._ud.report_filename
        file = 'Stocktake_uncollected_aged_report_20131206122050.xlsx'
        attach_file = os.path.join('nparcel', 'tests', 'files', file)
        self._ud.set_report_filename(attach_file)

        old_ws = self._ud.ws
        title = 'Toll Parcel Portal Stocktake Uncollected (Aged) Report'
        now = self._now.strftime('%d/%m/%Y')
        self._ud.set_ws({'title': title})

        old_recipients = self._ud.recipients
        self._ud.set_recipients(['loumar@tollgroup.com'])

        now = self._now.strftime('%d/%m/%Y %H:%M')
        self._ud.send_email(date_ts=self._now)

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
