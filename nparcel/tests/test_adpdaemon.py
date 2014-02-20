import unittest2
import tempfile
import os

import nparcel
from nparcel.utils.files import (copy_file,
                                 remove_files,
                                 get_directory_files_list)


class TestAdpDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._adpd = nparcel.AdpDaemon(pidfile=None)
        cls._adpd.emailer.set_template_base(os.path.join('nparcel',
                                                         'templates'))
        test_dir = os.path.join('nparcel', 'tests', 'files')
        xlsv_file = 'ADP-Bulk-Load.xlsx'
        cls._test_file = os.path.join(test_dir, xlsv_file)

    def test_init(self):
        """Initialise a AdpDaemon object.
        """
        msg = 'Not a nparcel.AdpDaemon object'
        self.assertIsInstance(self._adpd, nparcel.AdpDaemon, msg)

    def test_start_dry_loop(self):
        """On Delivery _start dry loop.
        """
        old_dry = self._adpd.dry
        old_file = self._adpd.file

        dir = tempfile.mkdtemp()
        test_file = os.path.join(dir, os.path.basename(self._test_file))
        copy_file(self._test_file, os.path.join(dir, test_file))

        # Start processing.
        self._adpd.config = nparcel.B2CConfig()
        headers = {'code': 'TP Code',
                   'dp_code': 'DP Code',
                   'name': 'ADP Name'}
        self._adpd.config.set_adp_headers(headers)
        self._adpd.set_dry()
        self._adpd.set_file(test_file)
        self._adpd._start(self._adpd.exit_event)

        # Clean up.
        self._adpd.config = None
        self._adpd._exit_event.clear()
        self._adpd.set_dry(old_dry)
        self._adpd.set_file(old_file)
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)

    def test_start_non_dry_loop(self):
        """On Delivery _start non dry loop.
        """
        dry = False

        old_file = self._adpd.file
        old_dry = self._adpd.dry
        old_batch = self._adpd.batch
        old_support_emails = list(self._adpd.support_emails)

        dir = tempfile.mkdtemp()
        test_file = os.path.join(dir, os.path.basename(self._test_file))
        copy_file(self._test_file, os.path.join(dir, test_file))

        # Start processing.
        self._adpd.config = nparcel.B2CConfig()
        headers = {'code': 'TP Code',
                   'dp_code': 'DP Code',
                   'name': 'ADP Name',
                   'address': 'Address',
                   'suburb': 'Suburb',
                   'state': 'State',
                   'postcode': 'Postcode',
                   'opening_hours': 'Opening Hours',
                   'notes': 'Notes',
                   'parcel_size_code': 'ADP Accepts Parcel Size',
                   'phone_nbr': 'Phone',
                   'contact': 'contact_name',
                   'email': 'Email',
                   'fax_nbr': 'Fax',
                   'status': 'Active'}
        self._adpd.config.set_adp_headers(headers)
        self._adpd.set_dry(dry)
        self._adpd.set_batch()
        self._adpd.set_file(test_file)
        # Add valid email address here if you want to verify support comms.
        self._adpd.set_support_emails(None)
        self._adpd._start(self._adpd.exit_event)

        # Clean up.
        self._adpd.config = None
        self._adpd.set_support_emails(old_support_emails)
        self._adpd.set_file(old_file)
        self._adpd.set_dry(old_dry)
        self._adpd.set_batch(old_batch)
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)
        self._adpd._exit_event.clear()

    def test_start_dry_loop_dir_based(self):
        """On Delivery _start dry loop - directory file input.
        """
        old_dry = self._adpd.dry
        old_adp_in_dir = self._adpd.adp_in_dirs
        old_adp_in_dirs = self._adpd.adp_in_dirs

        dir = tempfile.mkdtemp()
        test_file = os.path.join(dir, os.path.basename(self._test_file))
        copy_file(self._test_file, test_file)

        # Start processing.
        self._adpd.config = nparcel.B2CConfig()
        headers = {'code': 'TP Code',
                   'dp_code': 'DP Code',
                   'name': 'ADP Name'}
        self._adpd.config.set_adp_headers(headers)
        self._adpd.set_dry()
        self._adpd.set_adp_in_dirs([dir])
        self._adpd._start(self._adpd.exit_event)

        # Clean up.
        self._adpd._config = None
        self._adpd.set_dry(old_dry)
        self._adpd._exit_event.clear()
        self._adpd.set_adp_in_dirs(old_adp_in_dirs)
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)

    @classmethod
    def tearDownClass(cls):
        cls._adpd = None
        cls._test_file = None
