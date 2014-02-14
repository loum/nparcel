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
        cls._test_dir = os.path.join('nparcel', 'tests', 'files')

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
                                 'VIC_VANA_REP_20131108145146.txt'),
                    os.path.join(self._test_dir,
                                 'VIC_VANA_REP_20140214120000.txt')]
        msg = 'Priority report file should be found in listing'
        self.assertListEqual(sorted(received), sorted(expected), msg)

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
        self._ftp.config.set('ftp_t', 'pod', 'yes')
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

    def test_process_inbound_with_pod(self):
        """Test the process cycle for inbound transfer with POD.
        """
        t_files = get_directory_files_list(os.path.join(self._test_dir,
                                                        'returns'))
        dir = self._ftp_dir
        for f in t_files:
            copy_file(f, os.path.join(dir, os.path.basename(f)))

        # Prepare the config.
        filter = '.*_VANA_RE[PFI]_\d{14}\.txt'
        self._ftp.config.add_section('ftp_t')
        self._ftp.config.set('ftp_t', 'host', '127.0.0.1')
        self._ftp.config.set('ftp_t', 'port', '2121')
        self._ftp.config.set('ftp_t', 'user', 'tester')
        self._ftp.config.set('ftp_t', 'password', 'tester')
        self._ftp.config.set('ftp_t', 'direction', 'inbound')
        self._ftp.config.set('ftp_t', 'source', '')
        self._ftp.config.set('ftp_t', 'filter', filter)
        self._ftp.config.set('ftp_t', 'target', self._dir)
        self._ftp.config.set('ftp_t', 'pod', 'Yes')
        self._ftp.config.set('ftp_t', 'partial', 'YES')
        self._ftp.config.set('ftp_t', 'delete', 'yes')
        self._ftp._parse_config(file_based=False)

        self._ftp.process(dry=False)

        # Check FTP inbound directory (all files should be transfered).
        received = get_directory_files_list(self._dir)
        expected = [os.path.join(self._dir,
                                 os.path.basename(x)) for x in t_files]
        msg = 'FTP inbound directory list not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        remove_files(get_directory_files_list(self._dir))
        self._ftp.reset_config()

    def test_process_inbound_with_pod_to_multiple_targets(self):
        """Process cycle for inbound transfer with POD - multiple targets
        """
        t_files = get_directory_files_list(os.path.join(self._test_dir,
                                                        'returns'))
        dir = self._ftp_dir
        for f in t_files:
            copy_file(f, os.path.join(dir, os.path.basename(f)))

        # Prepare multiple targets.
        target_1 = tempfile.mkdtemp()
        target_2 = tempfile.mkdtemp()
        dirs = [target_1, target_2]

        # Prepare the config.
        filter = '.*_VANA_RE[PFI]_\d{14}\.txt'
        self._ftp.config.add_section('ftp_t')
        self._ftp.config.set('ftp_t', 'host', '127.0.0.1')
        self._ftp.config.set('ftp_t', 'port', '2121')
        self._ftp.config.set('ftp_t', 'user', 'tester')
        self._ftp.config.set('ftp_t', 'password', 'tester')
        self._ftp.config.set('ftp_t', 'direction', 'inbound')
        self._ftp.config.set('ftp_t', 'source', '')
        self._ftp.config.set('ftp_t', 'filter', filter)
        self._ftp.config.set('ftp_t', 'target', '%s,%s,%s' % (self._dir,
                                                              target_1,
                                                              target_2))
        self._ftp.config.set('ftp_t', 'pod', 'Yes')
        self._ftp.config.set('ftp_t', 'partial', 'YES')
        self._ftp.config.set('ftp_t', 'delete', 'yes')
        self._ftp._parse_config(file_based=False)

        self._ftp.process(dry=False)

        # Check FTP inbound directory (all files should be transfered).
        received = get_directory_files_list(self._dir)
        expected = [os.path.join(self._dir,
                                 os.path.basename(x)) for x in t_files]
        msg = 'FTP inbound directory list not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Check that the multi-directories also got their copy.
        xfered_report_files = get_directory_files_list(self._dir,
                                                       filter='.*\.txt$')
        expected = [os.path.basename(x) for x in xfered_report_files]
        for dir in dirs:
            tmp_files = get_directory_files_list(dir)
            received = [os.path.basename(x) for x in tmp_files]
            msg = 'Mutliple dir copy - %s listing error' % dir
            self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        remove_files(get_directory_files_list(self._dir))
        self._ftp.reset_config()
        for dir in dirs:
            remove_files(get_directory_files_list(dir))
            os.removedirs(dir)

    def test_process_inbound_without_pod(self):
        """Test the process cycle for inbound transfer WITHOUT POD.
        """
        t_files = get_directory_files_list(os.path.join(self._test_dir,
                                                        'returns'))
        dir = self._ftp_dir
        for f in t_files:
            copy_file(f, os.path.join(dir, os.path.basename(f)))

        # Prepare the config.
        filter = '.*_VANA_RE[PFI]_\d{14}\.txt'
        self._ftp.config.add_section('ftp_t')
        self._ftp.config.set('ftp_t', 'host', '127.0.0.1')
        self._ftp.config.set('ftp_t', 'port', '2121')
        self._ftp.config.set('ftp_t', 'user', 'tester')
        self._ftp.config.set('ftp_t', 'password', 'tester')
        self._ftp.config.set('ftp_t', 'direction', 'inbound')
        self._ftp.config.set('ftp_t', 'source', '')
        self._ftp.config.set('ftp_t', 'filter', filter)
        self._ftp.config.set('ftp_t', 'target', self._dir)
        self._ftp.config.set('ftp_t', 'pod', 'NO')
        self._ftp.config.set('ftp_t', 'partial', 'NO')
        self._ftp.config.set('ftp_t', 'delete', 'yes')
        self._ftp._parse_config(file_based=False)

        self._ftp.process(dry=False)

        # Check FTP inbound directory (only report files should be
        # transfered).
        received = get_directory_files_list(self._dir)
        expected = get_directory_files_list(os.path.join(self._test_dir,
                                                         'returns'), filter)
        expected = [os.path.join(self._dir,
                                 os.path.basename(x)) for x in expected]
        msg = 'FTP inbound directory list not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        remove_files(get_directory_files_list(self._ftp_dir))
        remove_files(get_directory_files_list(self._dir))
        self._ftp.reset_config()

    def test_process_inbound_pod_without_delete(self):
        """Test the process cycle for inbound transfer without delete.
        """
        t_files = get_directory_files_list(os.path.join(self._test_dir,
                                                        'returns'))
        dir = self._ftp_dir
        for f in t_files:
            copy_file(f, os.path.join(dir, os.path.basename(f)))

        # Prepare the config.
        filter = '.*_VANA_RE[PFI]_\d{14}\.txt'
        self._ftp.config.add_section('ftp_t')
        self._ftp.config.set('ftp_t', 'host', '127.0.0.1')
        self._ftp.config.set('ftp_t', 'port', '2121')
        self._ftp.config.set('ftp_t', 'user', 'tester')
        self._ftp.config.set('ftp_t', 'password', 'tester')
        self._ftp.config.set('ftp_t', 'direction', 'inbound')
        self._ftp.config.set('ftp_t', 'source', '')
        self._ftp.config.set('ftp_t', 'filter', filter)
        self._ftp.config.set('ftp_t', 'target', self._dir)
        self._ftp.config.set('ftp_t', 'pod', 'Yes')
        self._ftp.config.set('ftp_t', 'partial', 'YES')
        self._ftp.config.set('ftp_t', 'delete', 'NO')
        self._ftp._parse_config(file_based=False)

        self._ftp.process(dry=False)

        # Check FTP inbound directory (all files should be transfered).
        received = get_directory_files_list(self._dir)
        expected = [os.path.join(self._dir,
                                 os.path.basename(x)) for x in t_files]
        msg = 'FTP inbound directory list not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Check FTP source directory (all files should be intact).
        received = get_directory_files_list(self._ftp_dir)
        expected = [os.path.join(self._ftp_dir,
                                 os.path.basename(x)) for x in t_files]
        msg = 'FTP inbound directory list not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        remove_files(get_directory_files_list(self._ftp_dir))
        remove_files(get_directory_files_list(self._dir))
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
        expected = ['nparcel/tests/files/VIC_VANA_REP_20131108145146.txt',
                    'nparcel/tests/files/VIC_VANA_REP_20140214120000.txt']
        msg = 'POD report file get list'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def test_get_xfer_files_is_pod(self):
        """Get list of files to transfer - POD.
        """
        source = os.path.join('nparcel', 'tests', 'files')
        filter = 'VIC_VANA_REP_\d{14}\.txt'
        is_pod = True

        files = ['VIC_VANA_REP_20131108145146.txt',
                 'VIC_VANA_REP_20140214120000.txt',
                 '142828.ps',
                 '145563.ps',
                 '145601.ps',
                 '145661.ps',
                 '150000.ps',
                 '142828.png',
                 '145563.png',
                 '145601.png',
                 '145661.png',
                 '150000.png']
        received = self._ftp.get_xfer_files(source, filter, is_pod)
        expected = [os.path.join(source, x) for x in files]
        msg = 'POD report file get list'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def test_get_xfer_files_is_not_pod_T1250(self):
        """Get list of files to transfer - non POD T1250.
        """
        source = 'nparcel/tests/files'
        filter = 'T1250_TOLP_\d{14}\.txt$'
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
        t_files = get_directory_files_list(os.path.join(self._test_dir,
                                                        'returns'))
        for f in t_files:
            copy_file(f, os.path.join(dir, os.path.basename(f)))

        # Prepare the config.
        self._ftp.config.add_section('ftp_in')
        self._ftp.config.set('ftp_in', 'host', '127.0.0.1')
        self._ftp.config.set('ftp_in', 'port', '2121')
        self._ftp.config.set('ftp_in', 'user', 'tester')
        self._ftp.config.set('ftp_in', 'password', 'tester')
        self._ftp.config.set('ftp_in', 'filter', '.*_VANA_RE[PFI]_\d{14}\.txt')
        self._ftp.config.set('ftp_in', 'target', '')
        self._ftp.config.set('ftp_in', 'pod', 'yes')
        self._ftp._parse_config(file_based=False)

        self._ftp.inbound(self._ftp.xfers[0], dry=True)

        # Clean up.
        remove_files(get_directory_files_list(dir))
        self._ftp.reset_config()

    def test_get_files(self):
        """Get files from remote resource.
        """
        dir = self._ftp_dir
        t_files = get_directory_files_list(os.path.join(self._test_dir,
                                                        'returns'))
        remote_files = []
        for f in t_files:
            remote_files.append(os.path.basename(f))
            copy_file(f, os.path.join(dir, os.path.basename(f)))

        # Prepare the config.
        self._ftp.config.add_section('ftp_in')
        self._ftp.config.set('ftp_in', 'host', '127.0.0.1')
        self._ftp.config.set('ftp_in', 'port', '2121')
        self._ftp.config.set('ftp_in', 'user', 'tester')
        self._ftp.config.set('ftp_in', 'password', 'tester')
        self._ftp._parse_config(file_based=False)

        self._ftp.connect_resource(self._ftp.xfers[0])

        # No files to transfer.
        files_to_transfer = []
        received = self._ftp.get_files(files_to_transfer,
                                       target_dir=self._dir,
                                       dry=False)
        expected = []
        msg = 'No files to retrieve error'
        self.assertListEqual(received, expected, msg)

        # Single file transfer.
        files_to_transfer = ['VIC_VANA_REF_20131114073201.txt']
        received = self._ftp.get_files(files_to_transfer,
                                       target_dir=self._dir,
                                       dry=False)
        expected = get_directory_files_list(self._dir)
        ret = expected
        msg = 'Single file retrieved error'
        self.assertListEqual(received, expected, msg)

        # Report files to transfer.
        del expected[:]
        received = self._ftp.get_files(remote_files,
                                       target_dir=self._dir,
                                       dry=False)
        expected = get_directory_files_list(self._dir)
        msg = 'Retrieved multiple file list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._ftp.disconnect_resource()
        remove_files(get_directory_files_list(self._dir))
        remove_files(get_directory_files_list(dir))
        self._ftp.reset_config()

    def test_get_files_partial_context(self):
        """Retrieve remote files (partial context).
        """
        dir = self._ftp_dir
        remote_file = os.path.join(self._test_dir,
                                   'returns',
                                   'VIC_VANA_REP_20131114050106.txt')
        copy_file(remote_file,
                  os.path.join(dir, os.path.basename(remote_file)))

        # Prepare the config.
        self._ftp.config.add_section('ftp_in')
        self._ftp.config.set('ftp_in', 'host', '127.0.0.1')
        self._ftp.config.set('ftp_in', 'port', '2121')
        self._ftp.config.set('ftp_in', 'user', 'tester')
        self._ftp.config.set('ftp_in', 'password', 'tester')
        self._ftp._parse_config(file_based=False)

        self._ftp.connect_resource(self._ftp.xfers[0])

        # Single file transfer partial context.
        files_to_transfer = ['VIC_VANA_REP_20131114050106.txt']
        received = self._ftp.get_files(files_to_transfer,
                                       target_dir=self._dir,
                                       partial=True,
                                       dry=False)
        expected = [os.path.join(self._dir,
                                 os.path.basename(remote_file)) + '.tmp']
        msg = 'Single file (partial context) get_files() return error'
        self.assertListEqual(received, expected, msg)

        # Check the local directory content.
        received = get_directory_files_list(self._dir)
        expected = [os.path.join(self._dir,
                                 os.path.basename(remote_file) + '.tmp')]
        msg = 'Single file (partial context) retrieved error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._ftp.disconnect_resource()
        remove_files(get_directory_files_list(self._dir))
        remove_files(get_directory_files_list(dir))
        self._ftp.reset_config()

    def test_filter_file_list(self):
        """Filter file list.
        """
        t_dir = os.path.join(self._test_dir, 'returns')
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

    def test_get_pod_files(self):
        """Retrieve POD files.
        """
        dir = self._ftp_dir
        report_files = [os.path.join(self._test_dir,
                                     'returns',
                                     'VIC_VANA_REP_20131114050106.txt')]
        pod_file = os.path.join(self._test_dir,
                                'returns',
                                'P1014R0-0000NX32.ps')
        copy_file(pod_file, os.path.join(dir, os.path.basename(pod_file)))

        # Prepare the config.
        self._ftp.config.add_section('ftp_in')
        self._ftp.config.set('ftp_in', 'host', '127.0.0.1')
        self._ftp.config.set('ftp_in', 'port', '2121')
        self._ftp.config.set('ftp_in', 'user', 'tester')
        self._ftp.config.set('ftp_in', 'password', 'tester')
        self._ftp._parse_config(file_based=False)

        self._ftp.connect_resource(self._ftp.xfers[0])

        received = self._ftp.get_pod_files(report_files,
                                           target_dir=self._dir,
                                           remove=True,
                                           dry=False)
        expected = [os.path.join(self._dir, os.path.basename(pod_file))]
        msg = 'Retrieved POD file error'
        self.assertListEqual(received, expected, msg)

        # Try retrieving the same file.
        copy_file(pod_file, os.path.join(dir, os.path.basename(pod_file)))

        received = self._ftp.get_pod_files(report_files,
                                           target_dir=self._dir,
                                           remove=True,
                                           dry=False)

        # Clean up.
        self._ftp.disconnect_resource()
        remove_files(get_directory_files_list(self._dir))
        self._ftp.reset_config()

    def test_copy_to_multiple_directories(self):
        """Copy files into multiple directories.
        """
        dir1 = tempfile.mkdtemp()
        dir2 = tempfile.mkdtemp()
        dirs = [dir1, dir2]
        file_1_obj = tempfile.NamedTemporaryFile(suffix='.txt')
        file_2_obj = tempfile.NamedTemporaryFile(suffix='.txt')
        file_3_obj = tempfile.NamedTemporaryFile(suffix='.txt')
        files = [file_1_obj.name, file_2_obj.name, file_3_obj.name]

        self._ftp.copy_to_multiple_directories(dirs, files)

        # Check target dirs.
        for dir in dirs:
            tmp_files = get_directory_files_list(dir)
            received = [os.path.basename(x) for x in tmp_files]
            expected = [os.path.basename(x) for x in files]
            msg = 'Mutliple dir copy - %s listing error' % dir
            self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        file_1_obj.close()
        file_2_obj.close()
        file_3_obj.close()
        for dir in dirs:
            remove_files(get_directory_files_list(dir))
            os.removedirs(dir)

    @classmethod
    def tearDownClass(cls):
        cls._ftpserver.stop()

        del cls._test_dir
        cls._ftp = None
        del cls._ftp
        os.removedirs(cls._dir)
        del cls._dir
        os.removedirs(cls._archive_dir)
        del cls._archive_dir

        os.removedirs(cls._ftp_dir)
