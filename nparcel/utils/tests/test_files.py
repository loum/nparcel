import unittest2
import tempfile
import os

from nparcel.utils.files import (load_template,
                                 get_directory_files,
                                 get_directory_files_list,
                                 remove_files,
                                 check_filename)


class TestFiles(unittest2.TestCase):

    def test_load_template(self):
        """Load template.
        """
        received = load_template(template='test_template.t',
                                 base_dir='nparcel/utils/tests',
                                 replace='REPLACED')
        expected = 'Test Template REPLACED'
        msg = 'Template load error'
        self.assertEqual(received.rstrip(), expected, msg)

    def test_get_directory_files_no_directory(self):
        """Get directory file -- no directory.
        """
        dir = tempfile.mkdtemp()
        os.removedirs(dir)

        received = []
        for file in get_directory_files(dir):
            received.append(file)
        expected = []
        msg = 'Missing directory listing error'
        self.assertListEqual(received, expected, msg)

        received = get_directory_files_list(dir)
        expected = []
        msg = 'Missing directory listing error (list variant)'
        self.assertListEqual(received, expected, msg)

    def test_get_directory_files_no_files(self):
        """Get directory file -- no files.
        """
        dir = tempfile.mkdtemp()

        received = []
        for file in get_directory_files(dir):
            received.append(file)
        expected = []
        msg = 'Empty directory listing error'
        self.assertListEqual(received, expected, msg)

        received = get_directory_files_list(dir)
        expected = []
        msg = 'Empty directory listing error (list variant)'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        os.removedirs(dir)

    def test_get_directory_files(self):
        """Get directory files.
        """
        dir = tempfile.mkdtemp()
        file_obj = tempfile.NamedTemporaryFile(dir=dir)
        file = file_obj.name

        received = get_directory_files_list(dir)
        expected = [file]
        msg = 'Directory listing error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        file_obj.close()
        os.removedirs(dir)

    def test_get_directory_files_filtered(self):
        """Get directory files.
        """
        file_obj = tempfile.NamedTemporaryFile()
        dir = os.path.dirname(file_obj.name)
        file = file_obj.name

        filter_file = 'mts_delivery_report_20131018100758.csv'
        f = open(os.path.join(dir, filter_file), 'w')
        f.close()

        filter = 'mts_delivery_report_\d{14}\.csv'
        received = get_directory_files_list(os.path.dirname(file),
                                            filter=filter)
        expected = [os.path.join(dir, filter_file)]
        msg = 'Directory listing error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        remove_files(os.path.join(dir, filter_file))

    def test_check_filename(self):
        """Check Nparcel filename format.
        """
        format = 'T1250_TOL.*\.txt'
        # Priority.
        received = check_filename('T1250_TOLP_20130904061851.txt', format)
        msg = 'Priority Nparcel filename should validate True'
        self.assertTrue(received, msg)

        # Fast.
        received = check_filename('T1250_TOLF_VIC_20130904061851.txt',
                                  format)
        msg = 'Fast VIC Nparcel filename should validate True'
        self.assertTrue(received, msg)

        # Dodgy.
        received = check_filename('T1250_dodgy_20130904061851.txt', format)
        msg = 'Dodgy filename should validate False'
        self.assertFalse(received, msg)
