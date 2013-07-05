import unittest2
import tempfile
import os.path

from nparcel.utils.files import (RenamedTemporaryFile,
                                 dummy_filesystem,
                                 is_writable)


class TestUtilsFile(unittest2.TestCase):

    def test_is_writable_valid(self):
        """Test access to a writable file.
        """
        temp_fs = dummy_filesystem()
        fs = is_writable(temp_fs.name)
        self.assertNotEqual(fs, None)

    def test_dummy_filesystem(self):
        """Test the creation of the dummy filesystem.
        """
        temp_fs = dummy_filesystem(content='bananas')

        content = None
        with open(temp_fs.name) as fh:
            content = fh.read()

        msg = ''
        received = content
        expected = 'bananas'
        self.assertEqual(received, expected, msg)

    def test_file_context_manager(self):
        """Test grouping for the RenamedTemporaryFile class.
        """
        self.file_creation()

    def file_creation(self):
        """Test the creation of a file and its contents.
        """
        # Use the temporary file facility to generate a file name.
        test_tempfile = tempfile.NamedTemporaryFile()
        test_final_path = os.path.basename(test_tempfile.name)

        # This close should delete the file from the filesystem.
        # That's OK as we just want a sample filename for testing.
        test_tempfile.close()

        msg = 'Final path "%s" already exists' % test_final_path
        self.assertFalse(os.path.exists(test_final_path), msg)

        # Create a file with our RenamedTemporaryFile facility.
        with RenamedTemporaryFile(test_final_path) as f:
            f.write('stuff')

        # Temp file should now exist on the filesystem.
        msg = 'Final path "%s" does not exist' % test_final_path
        self.assertTrue(os.path.exists(test_final_path), msg)

        # Get the test file's contents.
        f_in = None
        test_file_contents = None
        try:
            f_in = open(test_final_path)
            test_file_contents = f_in.read()
            f_in.close()

            # Clean up.
            try:
                os.remove(test_final_path)
            except:
                pass
        except:
            pass

        # The file opens for reading.
        msg = 'Unable to open "%s" for reading' % test_final_path
        self.assertNotEqual(f_in, None, msg)

        # Test file contents should match.
        msg = 'Test file "%s" not as expected' % test_final_path
        self.assertEqual(test_file_contents, 'stuff', msg)

if __name__ == '__main_':
    unittest2.main()
