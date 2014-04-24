import unittest2
import tempfile
import os

import nparcel
from nparcel.utils.files import (remove_files,
                                 get_directory_files_list,
                                 copy_file)


class TestOnDeliveryDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._odd = nparcel.OnDeliveryDaemon(pidfile=None)

        cls._report_in_dirs = tempfile.mkdtemp()
        cls._odd.set_report_in_dirs([cls._report_in_dirs])

        cls._comms_dir = tempfile.mkdtemp()
        cls._odd.set_comms_dir(cls._comms_dir)
        cls._odd.set_business_units({'priority': 1,
                                     'fast': 2,
                                     'ipec': 3})
        dps = {'priority': ['Nparcel'],
               'fast': ['Nparcel'],
               'ipec': ['Nparcel', 'ParcelPoint']}
        cls._odd.set_comms_delivery_partners(dps)

        # Call up front to pre-load the DB.
        cls._odd.set_on_delivery(ts_db_kwargs=None)
        schema = cls._odd.od.ts_db.transsend.schema
        cls._odd.od.ts_db.create_table(name='v_nparcel_adp_connotes',
                                       schema=schema)
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixture_file = os.path.join(fixture_dir, 'transsend.py')
        cls._odd.od.ts_db.load_fixture(cls._odd.od.ts_db.transsend,
                                       fixture_file)

        db = cls._odd.od.db
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

        cls._test_dir = os.path.join('nparcel', 'tests', 'files')
        cls._test_file = 'TCD_Deliveries_20140207111019.DAT'
        cls._test_filepath = os.path.join(cls._test_dir, cls._test_file)

    def test_init(self):
        """Intialise a OnDeliveryDaemon object.
        """
        msg = 'Not a nparcel.OnDeliveryDaemon object'
        self.assertIsInstance(self._odd, nparcel.OnDeliveryDaemon, msg)

    def test_start_dry_loop(self):
        """On Delivery _start dry loop.
        """
        old_dry = self._odd.dry

        self._odd.set_dry()
        self._odd._start(self._odd.exit_event)

        # Clean up.
        self._odd.set_dry(old_dry)
        self._odd._exit_event.clear()

    def test_start_non_dry_loop_with_transsend(self):
        """Start non-dry loop -- transsend.
        """
        dry = False

        old_dry = self._odd.dry
        old_batch = self._odd.batch
        old_support_emails = self._odd.support_emails
        old_pe_comms_ids = self._odd.pe_bu_ids
        copy_file(os.path.join(self._test_dir, self._test_file),
                  os.path.join(self._report_in_dirs, self._test_file))

        # Start processing.
        self._odd.set_dry(dry)
        self._odd.set_batch()
        self._odd.set_pe_bu_ids((1, 2, 3))
        self._odd._start(self._odd._exit_event)

        # Comms files should have been created.
        received = get_directory_files_list(self._comms_dir)
        comms_files = ['email.10.pe',
                       'sms.10.pe',
                       'email.12.pe',
                       'sms.12.pe']
        expected = [os.path.join(self._comms_dir, x) for x in comms_files]
        msg = 'On Delivery (Primary Elect) comms file error'
        self.assertListEqual(sorted(expected), sorted(received), msg)

        # Clean up.
        remove_files(expected)
        remove_files(os.path.join(self._report_in_dirs, self._test_file))
        self._odd.set_dry(old_dry)
        self._odd.set_batch(old_batch)
        self._odd.set_support_emails(old_support_emails)
        self._odd.set_pe_bu_ids(old_pe_comms_ids)
        self._odd._exit_event.clear()

    def test_start_non_dry_loop_with_no_bu_ids_defined(self):
        """Start non-dry loop -- PE/SC 4 no BU defined.
        """
        dry = False

        old_dry = self._odd.dry
        old_batch = self._odd.batch
        old_support_emails = self._odd.support_emails
        copy_file(os.path.join(self._test_dir, self._test_file),
                  os.path.join(self._report_in_dirs, self._test_file))

        # Start processing.
        self._odd.set_dry(dry)
        self._odd.set_batch()
        self._odd._start(self._odd._exit_event)

        received = get_directory_files_list(self._comms_dir)
        expected = []
        msg = 'On Delivery (Primary Elect) no PE IDs comms file error'
        self.assertListEqual(sorted(expected), sorted(received), msg)

        # Clean up.
        remove_files(os.path.join(self._report_in_dirs, self._test_file))
        self._odd.set_dry(old_dry)
        self._odd.set_batch(old_batch)
        self._odd.set_support_emails(old_support_emails)
        self._odd._exit_event.clear()

    def test_start_non_dry_loop_with_transsend_with_sc4_comms(self):
        """Start non-dry loop -- transsend and service code 4 comms.
        """
        dry = False

        old_dry = self._odd.dry
        old_batch = self._odd.batch
        old_support_emails = self._odd.support_emails
        old_sc4_ids = self._odd.sc4_bu_ids
        copy_file(os.path.join(self._test_dir, self._test_file),
                  os.path.join(self._report_in_dirs, self._test_file))

        # Start processing.
        self._odd.set_dry(dry)
        self._odd.set_batch()
        self._odd.set_sc4_bu_ids((1,))
        self._odd._start(self._odd._exit_event)

        received = get_directory_files_list(self._comms_dir)
        comms_files = ['email.14.body',
                       'sms.14.body']
        expected = [os.path.join(self._comms_dir, x) for x in comms_files]
        msg = 'On Delivery (SC 4) comms file error'
        self.assertListEqual(sorted(expected), sorted(received), msg)

        # Clean up.
        remove_files(expected)
        remove_files(os.path.join(self._report_in_dirs, self._test_file))
        self._odd.set_dry(old_dry)
        self._odd.set_batch(old_batch)
        self._odd.set_support_emails(old_support_emails)
        self._odd.set_sc4_bu_ids(old_sc4_ids)
        self._odd._exit_event.clear()

    def test_start_non_dry_loop_with_transsend_with_sc4_comms_delay(self):
        """Start non-dry loop -- transsend and SC4 comms (delay template).
        """
        dry = False

        old_dry = self._odd.dry
        old_batch = self._odd.batch
        old_support_emails = self._odd.support_emails
        old_sc4_ids = self._odd.sc4_bu_ids
        old_sc4_delay_ids = self._odd.sc4_delay_bu_ids
        copy_file(os.path.join(self._test_dir, self._test_file),
                  os.path.join(self._report_in_dirs, self._test_file))

        # Start processing.
        self._odd.set_dry(dry)
        self._odd.set_batch()
        self._odd.set_sc4_bu_ids((1,))
        self._odd.set_sc4_delay_bu_ids((1,))
        self._odd._start(self._odd._exit_event)

        received = get_directory_files_list(self._comms_dir)
        comms_files = ['email.14.delay',
                       'sms.14.delay']
        expected = [os.path.join(self._comms_dir, x) for x in comms_files]
        msg = 'On Delivery (SC 4) comms file error'
        self.assertListEqual(sorted(expected), sorted(received), msg)

        # Clean up.
        remove_files(expected)
        remove_files(os.path.join(self._report_in_dirs, self._test_file))
        self._odd.set_dry(old_dry)
        self._odd.set_batch(old_batch)
        self._odd.set_support_emails(old_support_emails)
        self._odd.set_sc4_bu_ids(old_sc4_ids)
        self._odd.set_sc4_delay_bu_ids(old_sc4_delay_ids)
        self._odd._exit_event.clear()

    def test_get_files(self):
        """Get report files.
        """
        old_file_cache = self._odd.file_cache_size
        self._odd.set_file_cache_size(2)

        # Seed some files.
        old_files = ['TCD_Deliveries_20140207081019.DAT',
                     'TCD_Deliveries_20140207091019.DAT']
        files = ['TCD_Deliveries_20140207100019.DAT',
                 'TCD_Deliveries_20140207111019.DAT']
        for f in old_files + files:
            fh = open(os.path.join(self._report_in_dirs, f), 'w')
            fh.close()

        received = self._odd.get_files()
        expected = [os.path.join(self._report_in_dirs, x) for x in files]
        msg = 'TCD report files from get_files() error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._odd.set_file_cache_size(old_file_cache)
        remove_files([os.path.join(self._report_in_dirs, x) for x in files])

    def test_get_files_no_files_to_purge(self):
        """Get report files - no files to purge.
        """
        # Seed some files.
        files = ['TCD_Deliveries_20140207081019.DAT',
                 'TCD_Deliveries_20140207091019.DAT',
                 'TCD_Deliveries_20140207100019.DAT',
                 'TCD_Deliveries_20140207111019.DAT']
        for f in files:
            fh = open(os.path.join(self._report_in_dirs, f), 'w')
            fh.close()

        received = self._odd.get_files()
        expected = [os.path.join(self._report_in_dirs, x) for x in files]
        msg = 'TCD report files from get_files() error -- no purge'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        remove_files([os.path.join(self._report_in_dirs, x) for x in files])

    def test_get_files_no_files(self):
        """Get report files -- no files available.
        """
        # Seed some files.
        files = []
        for f in files:
            fh = open(os.path.join(self._report_in_dirs, f), 'w')
            fh.close()

        received = self._odd.get_files()
        expected = []
        msg = 'TCD report files from get_files() error -- no files'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        remove_files([os.path.join(self._report_in_dirs, x) for x in files])

    def test_get_files_empty_report_dir(self):
        """Get report files -- empty report directory.
        """
        received = self._odd.get_files()
        expected = []
        msg = 'Report files from get_files() error'
        self.assertListEqual(received, expected, msg)

    def test_delivery_partner_lookup(self):
        """Delivery partner lookups.
        """
        received = self._odd.delivery_partner_lookup(1)
        expected = ('Nparcel', )
        msg = 'Priority Delivery Partner lookup error'
        self.assertTupleEqual(received, expected, msg)

        received = self._odd.delivery_partner_lookup(3)
        expected = ('Nparcel', 'ParcelPoint')
        msg = 'IPEC Delivery Partner lookup error'
        self.assertTupleEqual(received, expected, msg)

        # No business units.
        old_bus = self._odd.business_units
        self._odd.set_business_units(None)

        received = self._odd.delivery_partner_lookup(3)
        expected = ()
        msg = 'Empty Business Units Delivery Partner lookup error'
        self.assertTupleEqual(received, expected, msg)

        # Clean up.
        self._odd.set_business_units(old_bus)

    def test_template_lookup(self):
        """Template lookups.
        """
        old_delay_templates = self._odd.sc4_delay_bu_ids

        self._odd.set_sc4_delay_bu_ids(None)
        received = self._odd.template_lookup(1)
        expected = 'body'
        msg = 'Priority template lookup error (SC4 tuple empty)'
        self.assertEqual(received, expected, msg)

        self._odd.set_sc4_delay_bu_ids((1,))
        received = self._odd.template_lookup(1)
        expected = 'delay'
        msg = 'Priority template lookup error (SC4 Priority set)'
        self.assertEqual(received, expected, msg)

        self._odd.set_sc4_delay_bu_ids((1, 2, 3))
        received = self._odd.template_lookup(1)
        expected = 'delay'
        msg = 'Priority template lookup error (SC4 all set)'
        self.assertEqual(received, expected, msg)

        self._odd.set_sc4_delay_bu_ids((1, 2, 3))
        received = self._odd.template_lookup(4)
        expected = 'body'
        msg = 'Priority template lookup error (SC4 all set)'
        self.assertEqual(received, expected, msg)

        # Clean up.
        self._odd.set_sc4_delay_bu_ids(old_delay_templates)

    @classmethod
    def tearDownClass(cls):
        cls._odd = None
        cls._test_file = None
        cls._test_filepath = None
        del cls._odd
        del cls._test_file
        del cls._test_filepath

        os.removedirs(cls._report_in_dirs)
        os.removedirs(cls._comms_dir)
        del cls._report_in_dirs
        del cls._comms_dir
