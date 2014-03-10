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
        cls._ed = nparcel.ExporterDaemon(pidfile=None)
        cls._ed.config = nparcel.ExporterB2CConfig()

        cls._ed.emailer.set_template_base(os.path.join('nparcel',
                                                       'templates'))

        # Call up front to pre-load the DB.
        cls._ed._exporter = nparcel.Exporter(**(cls._ed.exporter_kwargs))

        db = cls._ed._exporter.db
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixtures = [{'db': db.agent, 'fixture': 'agents.py'},
                    {'db': db.job, 'fixture': 'jobs.py'},
                    {'db': db.jobitem, 'fixture': 'jobitems.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Intialise a ExporterDaemon object.
        """
        msg = 'Not a nparcel.ExporterDaemon object'
        self.assertIsInstance(self._ed, nparcel.ExporterDaemon, msg)

    def test_start(self):
        """Start dry loop.
        """
        old_dry = self._ed.dry

        self._ed.set_dry()
        self._ed._start(self._ed.exit_event)

        # Clean up.
        self._ed.set_dry(old_dry)
        self._ed.exit_event.clear()

    def test_start_non_dry(self):
        """Start non-dry loop.
        """
        dry = False

        old_dry = self._ed.dry
        old_batch = self._ed.batch
        old_support_emails = list(self._ed.support_emails)
        old_config_exporter_dirs = self._ed.config.exporter_dirs
        old_config_file_formats = self._ed.config.exporter_file_formats

        test_file_dir = os.path.join('nparcel', 'tests', 'files')
        file = 'VIC_VANA_REP_20140214120000.txt'
        dir = tempfile.mkdtemp()
        copy_file(os.path.join(test_file_dir, file),
                  os.path.join(dir, file))
        filters = [file]

        # Start processing.
        self._ed.set_dry(dry)
        self._ed.set_batch()
        self._ed.config.set_exporter_dirs([dir])
        self._ed.config.set_exporter_file_formats(filters)
        # Add valid email address here if you want to verify support comms.
        self._ed.set_support_emails(['lou.markovski@gmail.com'])
        self._ed._start(self._ed.exit_event)

        # Clean up.
        self._ed.config.set_exporter_dirs(old_config_exporter_dirs)
        self._ed.config.set_exporter_file_formats(old_config_file_formats)
        self._ed.set_support_emails(old_support_emails)
        self._ed.set_dry(old_dry)
        self._ed.set_batch(old_batch)
        remove_files(get_directory_files_list(dir))
        self._ed.exit_event.clear()

    @classmethod
    def tearDownClass(cls):
        cls._ed = None
