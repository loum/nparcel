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
        test_file_dir = os.path.join('nparcel', 'tests', 'files', 'ftp')
        test_file = 'VIC_VANA_REP_20130812140736.txt'

        report = os.path.join(self._dir, test_file)
        copy_file(os.path.join(test_file_dir, test_file), report)

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

    def test_xfer_files_proxy(self):
        """Placeholder test to make sure that we can connect to via proxy.
        """
        # Enable this test, set remote credentials.
        remote_host = None
        user = None
        password = None
        target = None

        dir = tempfile.mkdtemp()
        self._ftp.config.add_section('ftp_t')
        self._ftp.config.set('ftp_t', 'host', str(remote_host))
        self._ftp.config.set('ftp_t', 'port', '21')
        self._ftp.config.set('ftp_t', 'user', str(user))
        self._ftp.config.set('ftp_t', 'password', str(password))
        self._ftp.config.set('ftp_t', 'source', dir)
        self._ftp.config.set('ftp_t', 'filter', 'T1250_TOLP_\d{14}\.txt')
        self._ftp.config.set('ftp_t', 'target', str(target))
        self._ftp.config.set('ftp_t', 'pod', 'False')
        self._ftp.config.set('ftp_t', 'proxy', 'proxy.toll.com.au')
        self._ftp._parse_config(file_based=False)

        files = []
        if (remote_host is not None and
            user is not None and
            password is not None):
            self._ftp.xfer_files(self._ftp.xfers[0], files, dry=True)

        # Clean up.
        os.removedirs(dir)
        self._ftp.reset_config()

    def test_inbound(self):
        """Inbound file transfer.
        """
        dir = self._ftp_dir
        t_files = get_directory_files_list('nparcel/tests/files/returns')
        for f in t_files:
            copy_file(f, os.path.join(dir, os.path.basename(f)))

        # Prepare the config.
        self._ftp.config.add_section('ftp_in')
        self._ftp.config.set('ftp_in', 'host', '127.0.0.1')
        self._ftp.config.set('ftp_in', 'port', '2121')
        self._ftp.config.set('ftp_in', 'user', 'tester')
        self._ftp.config.set('ftp_in', 'password', 'tester')
        self._ftp.config.set('ftp_in', 'filter', 'VIC_VANA_REP_\d{14}\.txt')
        self._ftp.config.set('ftp_in', 'target', '')
        self._ftp.config.set('ftp_in', 'pod', 'True')
        self._ftp._parse_config(file_based=False)

        self._ftp.inbound(self._ftp.xfers[0], dry=True)

        # Clean up.
        remove_files(get_directory_files_list(dir))
        self._ftp.reset_config()

    def test_filter_file_list(self):
        """Filter file list.
        """
        t_dir = os.path.join('nparcel', 'tests', 'files', 'returns')
        t_files = get_directory_files_list(t_dir)

        format = 'banana'
        received = self._ftp.filter_file_list(t_files, format)
        expected = []
        msg = '"%s" filter list error' % format
        self.assertListEqual(received, expected, msg)

        format = 'VIC_VANA_REP_\d{14}\.txt'
        received = self._ftp.filter_file_list(t_files, format)
        priority_rep_file = ['VIC_VANA_REP_20131114044105.txt',
                             'VIC_VANA_REP_20131114050106.txt']
        expected = [os.path.join(t_dir, x) for x in priority_rep_file]
        msg = '"%s" filter list error' % format
        self.assertListEqual(sorted(received), sorted(expected), msg)

        format = 'VIC_VANA_REI_\d{14}\.txt'
        received = self._ftp.filter_file_list(t_files, format)
        priority_rep_file = ['VIC_VANA_REI_20131114044602.txt',
                             'VIC_VANA_REI_20131114045103.txt',
                             'VIC_VANA_REI_20131114045604.txt']
        expected = [os.path.join(t_dir, x) for x in priority_rep_file]
        msg = '"%s" filter list error' % format
        self.assertListEqual(sorted(received), sorted(expected), msg)

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
