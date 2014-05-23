import unittest2
import tempfile
import os

import top
from top.utils.files import (copy_file,
                             remove_files,
                             get_directory_files_list)


class TestAdpDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._adpd = top.AdpDaemon(pidfile=None)
        cls._adpd.emailer.set_template_base(os.path.join('top',
                                                         'templates'))
        cls._adpd._config = top.AdpB2CConfig()
        headers = {'agent.code': 'TP Code',
                   'agent.dp_code': 'DP Code',
                   'agent.name': 'ADP Name',
                   'agent.address': 'Address',
                   'agent.suburb': 'Suburb',
                   'agent.state': 'State',
                   'agent.postcode': 'Postcode',
                   'agent.opening_hours': 'Opening Hours',
                   'agent.notes': 'Notes',
                   'agent.latitude': 'Latitude',
                   'agent.longitude': 'Longitude',
                   'agent.parcel_size_code': 'ADP Accepts Parcel Size',
                   'agent.phone_nbr': 'Phone',
                   'agent.contact_name': 'Contact',
                   'agent.email': 'Email',
                   'agent.fax_nbr': 'Fax',
                   'agent.status': 'Active',
                   'delivery_partner.id': 'DP Id',
                   'login_account.username': 'Username',
                   'login_account.status': 'Login Status'}
        cls._adpd._config.set_adp_headers(headers)
        delivery_partners = ['Nparcel',
                             'ParcelPoint',
                             'Toll',
                             'National Storage']
        cls._adpd._config.set_delivery_partners(delivery_partners)
        default_passwords = {'nparcel': 'aaaa',
                             'parcelpoint': 'bbbb',
                             'toll': 'cccc',
                             'national storage': 'dddd'}
        cls._adpd._config.set_adp_default_passwords(default_passwords)

        test_dir = os.path.join('top', 'tests', 'files')
        xlsv_file = 'ADP-Bulk-Load.xlsx'
        cls._test_file = os.path.join(test_dir, xlsv_file)
        new_xlsv_file = 'ADP-Bulk-Load-new.xlsx'
        cls._new_test_file = os.path.join(test_dir, new_xlsv_file)

    def test_init(self):
        """Initialise a AdpDaemon object.
        """
        msg = 'Not a top.AdpDaemon object'
        self.assertIsInstance(self._adpd, top.AdpDaemon, msg)

    def test_start_dry_loop(self):
        """ADP bulk load _start dry loop.
        """
        old_dry = self._adpd.dry
        old_file = self._adpd.file

        dir = tempfile.mkdtemp()
        test_file = os.path.join(dir, os.path.basename(self._test_file))
        copy_file(self._test_file, os.path.join(dir, test_file))

        # Start processing.
        self._adpd.set_dry()
        self._adpd.set_file(test_file)
        self._adpd._start(self._adpd.exit_event)

        # Clean up.
        self._adpd._exit_event.clear()
        self._adpd.set_dry(old_dry)
        self._adpd.set_file(old_file)
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)

    def test_start_non_dry_loop(self):
        """ADP bulkd load _start non dry loop.
        """
        dry = False

        old_file = self._adpd.file
        old_dry = self._adpd.dry
        old_batch = self._adpd.batch
        old_support_emails = list(self._adpd.support_emails)
        old_archive_dir = self._adpd.archive_dir

        dir = tempfile.mkdtemp()
        test_file = os.path.join(dir, os.path.basename(self._test_file))
        copy_file(self._test_file, os.path.join(dir, test_file))

        archive_dir = tempfile.mkdtemp()

        # Start processing.
        self._adpd.set_dry(dry)
        self._adpd.set_batch()
        self._adpd.set_file(test_file)
        self._adpd.set_archive_dir(archive_dir)
        # Add valid email address here if you want to verify support comms.
        self._adpd.set_support_emails([])
        self._adpd._start(self._adpd.exit_event)

        # Clean up.
        self._adpd.set_support_emails(old_support_emails)
        self._adpd.set_file(old_file)
        self._adpd.set_dry(old_dry)
        self._adpd.set_batch(old_batch)
        self._adpd.set_archive_dir(archive_dir)
        os.removedirs(dir)
        remove_files(get_directory_files_list(os.path.join(archive_dir,
                                                           'adp')))
        os.removedirs(os.path.join(archive_dir, 'adp'))
        self._adpd._adp.db.rollback()
        self._adpd._exit_event.clear()

    def test_start_update_non_dry_loop(self):
        """ADP bulk load update _start non dry loop.
        """
        dry = False

        old_file = self._adpd.file
        old_dry = self._adpd.dry
        old_batch = self._adpd.batch
        old_support_emails = list(self._adpd.support_emails)
        old_archive_dir = self._adpd.archive_dir

        dir = tempfile.mkdtemp()
        test_file = os.path.join(dir, os.path.basename(self._test_file))
        copy_file(self._test_file, os.path.join(dir, test_file))

        archive_dir = tempfile.mkdtemp()

        # Start processing.
        self._adpd.set_dry(dry)
        self._adpd.set_batch()
        self._adpd.set_file(test_file)
        self._adpd.set_archive_dir(archive_dir)
        # Add valid email address here if you want to verify support comms.
        self._adpd.set_support_emails([])
        self._adpd._start(self._adpd.exit_event)
        self._adpd._exit_event.clear()

        # ... now perform an update.
        old_mode = self._adpd.mode
        self._adpd.set_mode('update')
        new_test_file = os.path.join(dir,
                                     os.path.basename(self._new_test_file))
        copy_file(self._new_test_file, os.path.join(dir, new_test_file))
        self._adpd.set_file(new_test_file)
        self._adpd._start(self._adpd.exit_event)

        # And check the results.
        sql = """SELECT dp_code,
       username,
       name,
       address,
       suburb,
       latitude,
       longitude
FROM agent WHERE code = 'V001'"""
        self._adpd._adp.db(sql)
        received = list(self._adpd.adp.db.rows())
        expected = [('VHAW050',
                     'VHAW050',
                     'New Auburn Newsagency',
                     '100 New Auburn Road',
                     'HAWTHORN EAST ',
                     -35.822864000000003,
                     155.045278)]
        msg = 'Updated ADP for code "V001" error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._adpd.set_support_emails(old_support_emails)
        self._adpd.set_file(old_file)
        self._adpd.set_dry(old_dry)
        self._adpd.set_batch(old_batch)
        self._adpd.set_archive_dir(archive_dir)
        self._adpd.set_mode(old_mode)
        os.removedirs(dir)
        remove_files(get_directory_files_list(os.path.join(archive_dir,
                                                           'adp')))
        os.removedirs(os.path.join(archive_dir, 'adp'))
        self._adpd._adp.db.rollback()
        self._adpd._exit_event.clear()

    def test_start_dry_loop_dir_based(self):
        """ADP bulk load _start dry loop - directory file input.
        """
        old_dry = self._adpd.dry
        old_adp_in_dir = self._adpd.adp_in_dirs
        old_adp_in_dirs = self._adpd.adp_in_dirs

        dir = tempfile.mkdtemp()
        test_file = os.path.join(dir, os.path.basename(self._test_file))
        copy_file(self._test_file, test_file)

        # Start processing.
        self._adpd.set_dry()
        self._adpd.set_adp_in_dirs([dir])
        self._adpd._start(self._adpd.exit_event)

        # Clean up.
        self._adpd.set_dry(old_dry)
        self._adpd._exit_event.clear()
        self._adpd.set_adp_in_dirs(old_adp_in_dirs)
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)

    @classmethod
    def tearDownClass(cls):
        cls._adpd = None
        cls._test_file = None
        cls._new__test_file = None
