import unittest2
import tempfile
import os

import top
from top.utils.files import remove_files


class TestOnDelivery(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._comms_dir = tempfile.mkdtemp()
        cls._on = top.OnDelivery(comms_dir=cls._comms_dir)
        cls._on.ts_db.create_table(name='v_nparcel_adp_connotes',
                                   schema=cls._on.ts_db.transsend.schema)
        fixture_dir = os.path.join('top', 'tests', 'fixtures')
        fixture_file = os.path.join(fixture_dir, 'transsend.py')
        cls._on.ts_db.load_fixture(cls._on.ts_db.transsend, fixture_file)

        test_dir = os.path.join('top', 'tests', 'files')
        test_file = 'TCD_Deliveries_20140207111019.DAT'
        cls._test_file = os.path.join(test_dir, test_file)

        db = cls._on.db
        fixtures = [{'db': db.agent, 'fixture': 'agents.py'},
                    {'db': db.delivery_partner,
                     'fixture': 'delivery_partners.py'},
                    {'db': db.parcel_size, 'fixture': 'parcel_sizes.py'},
                    {'db': db.job, 'fixture': 'jobs.py'},
                    {'db': db.identity_type, 'fixture': 'identity_type.py'},
                    {'db': db.jobitem, 'fixture': 'jobitems.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Initialise a OnDelivery object.
        """
        msg = 'Object is not a top.OnDelivery'
        self.assertIsInstance(self._on, top.OnDelivery, msg)

    def test_get_primary_elect_job_item_id_not_pe(self):
        """jobitem.id's of connote that is not a primary elect job.
        """
        received = self._on.get_primary_elect_job_item_id('con_001')
        expected = []
        msg = 'Non-primary elect job should produce empty list'
        self.assertListEqual(received, expected, msg)

    def test_get_primary_elect_job_item_id_valid_pe(self):
        """jobitem.id's of connote that is a primary elect job.
        """
        connote = 'pe_connote'
        received = self._on.get_primary_elect_job_item_id(connote)
        expected = [3]
        msg = 'Primary elect job should produce ids'
        self.assertListEqual(received, expected, msg)

    def test_get_primary_elect_job_item_id_valid_pe_no_comms(self):
        """jobitem.id's of connote that is a primary elect job -- no comms.
        """
        received = self._on.get_primary_elect_job_item_id('con_003')
        expected = []
        msg = 'Primary elect job no recipients should produce empty list'
        self.assertListEqual(received, expected, msg)

    def test_process_dry_run(self):
        """Check processing -- dry run.
        """
        dry = True

        service_code = 3
        bu_ids = (1, 2, 3)
        in_files = [self._test_file]
        received = self._on.process(template='pe',
                                    service_code=service_code,
                                    bu_ids=bu_ids,
                                    in_files=in_files,
                                    dry=dry)
        expected = []
        msg = 'List of processed primary elect items incorrect'
        self.assertListEqual(received, expected, msg)

    def test_process(self):
        """Check processing.
        """
        dry = False

        service_code = 3
        bu_ids = (1, 2, 3)
        in_files = [self._test_file]
        kwargs = {'template': 'pe',
                  'service_code': service_code,
                  'bu_ids': bu_ids,
                  'in_files': in_files,
                  'delivery_partners': ('Nparcel', ),
                  'dry': dry}
        received = self._on.process(**kwargs)
        expected = [10, 12]
        msg = 'List of processed primary elect items incorrect'
        self.assertListEqual(received, expected, msg)

        # Check that the comms files were written out.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        expected = [os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('email', 10, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('sms', 10, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('email', 12, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('sms', 12, 'pe')]
        msg = 'Comms directory file list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Cleanup.
        remove_files(received)

    def test_process_erred_comms(self):
        """Check processing -- error comms already exists.
        """
        dry = False

        comms_err_file = os.path.join(self._comms_dir,
                                      'email.%d.pe.err' % 10)
        fh = open(comms_err_file, 'w')
        fh.close()

        kwargs = {'template': 'pe',
                  'service_code': 3,
                  'bu_ids': (1, 2, 3),
                  'delivery_partners': ('Nparcel', ),
                  'in_files': [self._test_file],
                  'dry': dry}
        received = self._on.process(**kwargs)
        expected = [12]
        msg = 'OnDelivery (erred comms) processing error'
        self.assertListEqual(received, expected, msg)

        # Check that the comms files were written out.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        received = [x for x in received if x != comms_err_file]
        expected = [os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('email', 12, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('sms', 12, 'pe')]
        msg = 'OnDelivery (erred comms) comms directory list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Cleanup.
        remove_files(received)
        remove_files(comms_err_file)

    def test_process_comms_exists(self):
        """Check processing -- comms already exists.
        """
        dry = False

        comms_err_file = os.path.join(self._comms_dir, 'email.%d.pe' % 12)
        fh = open(comms_err_file, 'w')
        fh.close()

        kwargs = {'template': 'pe',
                  'service_code': 3,
                  'bu_ids': (1, 2, 3),
                  'delivery_partners': ('Nparcel', ),
                  'in_files': [self._test_file],
                  'dry': dry}
        received = self._on.process(**kwargs)
        expected = [10]
        msg = 'OnDelivery (comms already exists) processing error'
        self.assertListEqual(received, expected, msg)

        # Check that the comms files were written out.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        received = [x for x in received if x != comms_err_file]
        expected = [os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('email', 10, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('sms', 10, 'pe')]
        msg = 'OnDelivery (comms already exists) comms directory list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Cleanup.
        remove_files(received)
        remove_files(comms_err_file)

    def test_process_inline(self):
        """Check processing.
        """
        dry = False

        job_items = [(5, 'ANWD011307', 'ANWD011307001')]
        kwargs = {'template': 'pe',
                  'service_code': 3,
                  'bu_ids': (1, 2, 3),
                  'job_items': job_items,
                  'in_files': [self._test_file],
                  'delivery_partners': ('Nparcel', ),
                  'dry': dry}
        received = self._on.process(**kwargs)
        expected = [5]
        msg = 'List of processed primary elect items incorrect'
        self.assertListEqual(received, expected, msg)

        # Check that the comms files were written out.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        expected = [os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('email', 5, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('sms', 5, 'pe')]
        msg = 'Comms directory file list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Cleanup.
        remove_files(received)

    def test_process_no_tcd_file(self):
        """Check processing -- no TCD file.
        """
        dry = False

        kwargs = {'template': 'pe',
                  'service_code': 3,
                  'bu_ids': (1, 2, 3),
                  'delivery_partners': ('Nparcel', ),
                  'dry': dry}
        received = self._on.process(**kwargs)
        expected = [12]
        msg = 'Processed primary elect should return values'
        self.assertListEqual(received, expected, msg)

        # Check that the comms files were written out.
        received = [os.path.join(self._comms_dir,
                                 x) for x in os.listdir(self._comms_dir)]
        expected = [os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('email', 12, 'pe'),
                    os.path.join(self._comms_dir, '%s.%d.%s') %
                    ('sms', 12, 'pe')]
        msg = 'Comms directory file list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Cleanup.
        remove_files(received)

    def test_connote_delivered_no_db(self):
        """Query delivered status against TransSend.
        """
        connote = 'APLD029228'
        item_nbr = 'APLD029228001'

        received = self._on.connote_delivered(connote, item_nbr)
        msg = 'TransSend delivery check should be False -- no DB conn'
        self.assertFalse(received)

    def test_connote_delivered_not_delivered(self):
        """Query delivered status against TransSend -- not delivered.
        """
        connote = 'APLD029228'
        item_nbr = 'APLD029228001'

        received = self._on.connote_delivered(connote, item_nbr)
        msg = 'TransSend delivery check should be False'
        self.assertFalse(received)

    def test_connote_delivered_delivered(self):
        """Query delivered status against TransSend -- delivered.
        """
        connote = 'ANWD011307'
        item_nbr = 'ANWD011307001'

        received = self._on.connote_delivered(connote, item_nbr)
        msg = 'TransSend delivery check should be True'
        self.assertTrue(received)

    def test_connote_delivered_delivered_with_scanned_desc_keys(self):
        """Query delivered status against TransSend -- delivered.
        """
        old_scan_keys = self._on.scan_desc_keys
        self._on.set_scan_desc_keys(['IDS - TOLL FAST GRAYS ONLINE'])

        connote = 'IANZ012769'
        item_nbr = 'IANZ012769'

        received = self._on.connote_delivered(connote, item_nbr)
        msg = 'TransSend delivery check should be True'
        self.assertFalse(received)

        # Clean up.
        self._on.set_scan_desc_keys(old_scan_keys)

    @classmethod
    def tearDownClass(cls):
        cls._on = None
        del cls._on
        os.removedirs(cls._comms_dir)
        del cls._comms_dir
        del cls._test_file
