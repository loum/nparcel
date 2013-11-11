import unittest2
import os
import tempfile
import threading

import nparcel
from nparcel.utils.files import (copy_file,
                                 get_directory_files_list,
                                 remove_files)
from nparcel.pyftpdlib import ftpserver


class FtpServer(object):

    exit_event = threading.Event()
    dir = None

    def __init__(self, dir=dir):
        self.dir = dir

        authorizer = ftpserver.DummyAuthorizer()
        authorizer.add_user('tester',
                            password='tester',
                            homedir=dir,
                            perm='elradfmw')
        handler = ftpserver.FTPHandler
        handler.authorizer = authorizer

        address = ('127.0.0.1', 2121)
        self.server = ftpserver.FTPServer(address, handler)

    def start(self, exit_event):
        while not self.exit_event.isSet():
            self.server.serve_forever(timeout=0.1, count=1)

    def stop(self):
        self.exit_event.set()


class TestFtp(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up the FTP server.
        cls._ftp_dir = tempfile.mkdtemp()
        cls._ftpserver = FtpServer(cls._ftp_dir)
        t = threading.Thread(target=cls._ftpserver.start,
                             args=(cls._ftpserver.exit_event, ))
        t.start()

        cls._ftp = nparcel.Ftp()
        cls._test_dir = 'nparcel/tests/files'
        cls._priority_file = os.path.join(cls._test_dir,
                                          'VIC_VANA_REP_20131108145146.txt')

        # Create a temporary directory structure.
        cls._dir = tempfile.mkdtemp()
        cls._archive_dir = tempfile.mkdtemp()
        cls._ftp.set_archive_dir(cls._archive_dir)

    def test_init(self):
        """Initialise an FTP object.
        """
        msg = 'Object is not an nparcel.Ftp'
        self.assertIsInstance(self._ftp, nparcel.Ftp, msg)

    def test_parse_config_items(self):
        """Verify required configuration items.
        """
        self._ftp.config.add_section('ftp_priority')
        self._ftp.config.add_section('ftp_other')
        self._ftp.config.add_section('dummy')
        self._ftp._parse_config(file_based=False)

        # Check against expected config items.
        msg = 'Transfer sections not as expected'
        received = self._ftp.xfers
        expected = ['ftp_priority', 'ftp_other']
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._ftp.reset_config()

    def test_get_report_file_no_files(self):
        """Check directory for report files -- no files defined.
        """
        received = []
        for file in self._ftp.get_report_file(self._dir):
            received.append(file)
        msg = 'No reports should be found in an empty directory'
        self.assertListEqual(received, [], msg)

    def test_get_report_file(self):
        """Check directory for report files -- valid file defined.
        """
        filter = 'VIC_VANA_REP_\d{14}\.txt'
        received = []
        for file in self._ftp.get_report_file(self._test_dir, filter):
            received.append(file)
        expected = [os.path.join(self._test_dir,
                                 'VIC_VANA_REP_20131108145146.txt')]
        msg = 'Priority report file should be found in listing'
        self.assertListEqual(received, expected, msg)

        del (received[:], expected[:])
        received = expected = []
        filter = 'VIC_VANA_REI_\d{14}\.txt'
        received = []
        for file in self._ftp.get_report_file(self._test_dir, filter):
            received.append(file)
        expected = [os.path.join(self._test_dir,
                                 'VIC_VANA_REI_20131108145146.txt')]
        msg = 'Ipec report file should be found in listing'
        self.assertListEqual(received, expected, msg)

    def test_get_report_file_ids(self):
        """Check directory for report files -- valid file defined.
        """
        report = os.path.join(self._dir, 'VIC_VANA_REP_20130812140736.txt')
        fh = open(report, 'w')
        fh.write('REF1|JOB_KEY|PICKUP_TIME|PICKUP_POD|IDENTITY_TYPE|IDENTITY_DATA\n')
        fh.write('ALHZ104346|5|2013-02-01 01:23:45|UNCOLLECTED PARCEL DATACLEANUP|Other|0000')
        fh.close()

        received = self._ftp.get_report_file_ids(report)
        expected = ['5']
        msg = 'Report file should be found in directory'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        remove_files(report)

    def test_archive_file(self):
        """Archive file.
        """
        #temp_file = tempfile.NamedTemporaryFile()
        #temp_file_name = temp_file.name
        test_file = os.path.join(self._dir, 'tester')
        fh = open(test_file, 'w')
        fh.close()

        received = self._ftp.archive_file(test_file, dry=False)
        msg = 'File archive should return True'
        self.assertTrue(received, msg)

        # Check the archive directory.
        files = os.listdir(self._ftp.archive_dir)
        received = [os.path.join(self._ftp.archive_dir, x) for x in files]
        expected = [os.path.join(self._ftp.archive_dir,
                                 os.path.basename(test_file))]
        msg = 'Archive directory contents not as expected'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        remove_files(received)

    def test_process(self):
        """Test the process cycle.
        """
        t_files = ['VIC_VANA_REP_20131108145146.txt',
                   '142828.ps',
                   '145563.ps',
                   '145601.ps',
                   '145661.ps']
        dir = tempfile.mkdtemp()
        for f in t_files:
            copy_file(os.path.join(self._test_dir, f), os.path.join(dir, f))

        # Prepare the config.
        self._ftp.config.add_section('ftp_t')
        self._ftp.config.set('ftp_t', 'host', '127.0.0.1')
        self._ftp.config.set('ftp_t', 'port', '2121')
        self._ftp.config.set('ftp_t', 'user', 'tester')
        self._ftp.config.set('ftp_t', 'password', 'tester')
        self._ftp.config.set('ftp_t', 'source', dir)
        self._ftp.config.set('ftp_t', 'filter', 'VIC_VANA_REP_\d{14}\.txt')
        self._ftp.config.set('ftp_t', 'target', '')
        self._ftp.config.set('ftp_t', 'pod', 'True')
        self._ftp._parse_config(file_based=False)

        self._ftp.process(dry=False)

        # Check archive directory.
        received = get_directory_files_list(self._ftp.archive_dir)
        expected = [os.path.join(self._archive_dir, x) for x in t_files]
        msg = 'Archive directory list not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Check FTP inbound directory.
        received = get_directory_files_list(self._ftpserver.dir)
        expected = [os.path.join(self._ftpserver.dir, x) for x in t_files]
        msg = 'FTP inbound directory list not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        for f in t_files:
            remove_files(os.path.join(self._ftp_dir, f))
            remove_files(os.path.join(self._ftp.archive_dir, f))
        os.removedirs(dir)
        self._ftp.reset_config()

    def test_process_T1250(self):
        """Test the process cycle for T1250.
        """
        t_files = ['T1250_TOLP_20130413135756.txt']
        dir = tempfile.mkdtemp()
        for f in t_files:
            copy_file(os.path.join(self._test_dir, f), os.path.join(dir, f))

        # Prepare the config.
        self._ftp.config.add_section('ftp_t')
        self._ftp.config.set('ftp_t', 'host', '127.0.0.1')
        self._ftp.config.set('ftp_t', 'port', '2121')
        self._ftp.config.set('ftp_t', 'user', 'tester')
        self._ftp.config.set('ftp_t', 'password', 'tester')
        self._ftp.config.set('ftp_t', 'source', dir)
        self._ftp.config.set('ftp_t', 'filter', 'T1250_TOLP_\d{14}\.txt')
        self._ftp.config.set('ftp_t', 'target', '')
        self._ftp.config.set('ftp_t', 'pod', 'False')
        self._ftp._parse_config(file_based=False)

        self._ftp.process(dry=False)

        # Check archive directory.
        received = get_directory_files_list(self._ftp.archive_dir)
        expected = [os.path.join(self._archive_dir, x) for x in t_files]
        msg = 'Archive directory list not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Check FTP inbound directory.
        received = get_directory_files_list(self._ftpserver.dir)
        expected = [os.path.join(self._ftpserver.dir, x) for x in t_files]
        msg = 'FTP inbound directory list not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        for f in t_files:
            remove_files(os.path.join(self._ftp_dir, f))
            remove_files(os.path.join(self._ftp.archive_dir, f))
        os.removedirs(dir)
        self._ftp.reset_config()

    def test_get_xfer_files_is_not_pod(self):
        """Get list of files to transfer - non POD.
        """
        source = 'nparcel/tests/files'
        filter = 'VIC_VANA_REP_\d{14}\.txt'
        is_pod = False

        received = self._ftp.get_xfer_files(source, filter, is_pod)
        expected = ['nparcel/tests/files/VIC_VANA_REP_20131108145146.txt']
        msg = 'POD report file get list'
        self.assertListEqual(received, expected, msg)

    def test_get_xfer_files_is_pod(self):
        """Get list of files to transfer - POD.
        """
        source = 'nparcel/tests/files'
        filter = 'VIC_VANA_REP_\d{14}\.txt'
        is_pod = True

        files = ['VIC_VANA_REP_20131108145146.txt',
                 '142828.ps',
                 '145563.ps',
                 '145601.ps',
                 '145661.ps',
                 '142828.png',
                 '145563.png',
                 '145601.png',
                 '145661.png']
        received = self._ftp.get_xfer_files(source, filter, is_pod)
        expected = [os.path.join(source, x) for x in files]
        msg = 'POD report file get list'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def test_get_xfer_files_is_not_pod_T1250(self):
        """Get list of files to transfer - non POD T1250.
        """
        source = 'nparcel/tests/files'
        filter = 'T1250_TOLP_\d{14}\.txt'
        is_pod = False

        received = self._ftp.get_xfer_files(source, filter, is_pod)
        expected = ['nparcel/tests/files/T1250_TOLP_20130413135756.txt']
        msg = 'POD report file get list'
        self.assertListEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._ftpserver.stop()

        del cls._test_dir
        del cls._priority_file
        cls._ftp = None
        del cls._ftp
        os.removedirs(cls._dir)
        del cls._dir
        os.removedirs(cls._archive_dir)
        del cls._archive_dir

        os.removedirs(cls._ftp_dir)
