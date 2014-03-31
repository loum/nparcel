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
        cls._ed.set_business_units({'priority': 1, 'fast': 2, 'ipec': 3})
        cls._ed.config = nparcel.ExporterB2CConfig()
        cls._ed.config.set_cond({'tolp': '000100000000010110',
                                 'tolf': '000101100000010110',
                                 'toli': '100010000000010110'})
        cls._ed.config.set_file_bu({'tolp': 1,
                                    'tolf': 2,
                                    'tolf_nsw': 2,
                                    'tolf_vic': 2,
                                    'tolf_qld': 2,
                                    'tolf_sa': 2,
                                    'tolf_wa': 2,
                                    'tolf_act': 2,
                                    'toli': 3})

        # Signature dir.
        cls._signature_dir = tempfile.mkdtemp()
        cls._ed.config.set_signature_dir(cls._signature_dir)
        cls._sig_files = ['1.ps', '1.png', '5.ps', '5.png']
        for f in cls._sig_files:
            fh = open(os.path.join(cls._signature_dir, f), 'w')
            fh.close()

        # Exporter file closure dirs.
        cls._exporter_dir = tempfile.mkdtemp()
        cls._ed.config.set_exporter_dirs([cls._exporter_dir])

        # Staging base.
        cls._staging_dir = tempfile.mkdtemp()
        cls._ed.config.set_staging_base(cls._staging_dir)

        # Archive directory.
        cls._archive_dir = tempfile.mkdtemp()
        cls._ed.config.set_archive_dir(cls._archive_dir)

        cls._ed.emailer.set_template_base(os.path.join('nparcel',
                                                       'templates'))

        # Call up front to pre-load the DB.
        cls._ed._exporter = nparcel.Exporter(**(cls._ed.exporter_kwargs))
        cls._ed.set_exporter_fields({'tolp': '0,1,2,3,4,5,6',
                                     'tolf': '0,1,2,3,4,5,6',
                                     'toli': '0,1,2,3,4,5,6,7'})

        db = cls._ed._exporter.db
        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        fixtures = [{'db': db.agent, 'fixture': 'agents.py'},
                    {'db': db.identity_type,
                     'fixture': 'identity_type.py'},
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
        self._ed.set_support_emails([])
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
        del cls._ed
        # Hardwired for now until we can think of a better way ...
        sig_dir_1 = os.path.join(cls._archive_dir,
                                 'signature',
                                 'c4',
                                 'c4ca',
                                 'c4ca42',
                                 'c4ca4238')
        remove_files(get_directory_files_list(sig_dir_1))
        sig_dir_5 = os.path.join(cls._archive_dir,
                                 'signature',
                                 'e4',
                                 'e4da',
                                 'e4da3b',
                                 'e4da3b7f')
        remove_files(get_directory_files_list(sig_dir_5))
        os.removedirs(sig_dir_1)
        os.removedirs(sig_dir_5)
        os.removedirs(cls._exporter_dir)
        for dir in ['priority', 'fast', 'ipec']:
            out_dir = os.path.join(cls._staging_dir, dir, 'out')
            remove_files(get_directory_files_list(out_dir))
            os.removedirs(out_dir)
