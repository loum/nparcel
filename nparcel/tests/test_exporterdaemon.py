import unittest2
import os
import tempfile

import nparcel
from nparcel.utils.files import (copy_file,
                                 remove_files,
                                 get_directory_files_list)


class TestExporterDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        config = os.path.join('nparcel', 'conf', 'nparceld.conf')
        cls._ed = nparcel.ExporterDaemon(pidfile=None, config=config)
        cls._ed.emailer.set_template_base(os.path.join('nparcel',
                                                       'templates'))

    def test_init(self):
        """Intialise a ExporterDaemon object.
        """
        msg = 'Not a nparcel.ExporterDaemon object'
        self.assertIsInstance(self._ed, nparcel.ExporterDaemon, msg)

    def test_start(self):
        self._ed.set_dry()
        self._ed.set_batch()
        self._ed._start(self._ed.exit_event)

    def test_start_non_dry(self):
        dry = False

        test_file_dir = os.path.join('nparcel', 'tests', 'files')
        dir = tempfile.mkdtemp()
        file = 'VIC_VANA_REP_20140214120000.txt'
        copy_file(os.path.join(test_file_dir, file),
                  os.path.join(dir, file))
        filters = [file]

        old_dry = self._ed.dry
        old_support_emails = list(self._ed.support_emails)
        old_config_exporter_dirs = self._ed.config.exporter_dirs
        old_config_file_formats = self._ed.config.exporter_file_formats

        # Start processing.
        self._ed.set_dry(dry)
        self._ed.set_batch()
        self._ed.config.set_exporter_dirs([dir])
        self._ed.config.set_exporter_file_formats(filters)
        # Add valid email address here if you want to verify support comms.
        self._ed.set_support_emails(None)
        self._ed._start(self._ed.exit_event)

        # Clean up.
        self._ed.config.set_exporter_dirs(old_config_exporter_dirs)
        self._ed.config.set_exporter_file_formats(old_config_file_formats)
        self._ed.set_support_emails(old_support_emails)
        self._ed.set_dry(old_dry)
        remove_files(get_directory_files_list(dir))

    @classmethod
    def tearDownClass(cls):
        cls._ed = None
