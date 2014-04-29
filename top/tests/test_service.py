import unittest2
import tempfile
import os

import top

from top.utils.files import remove_files


class TestService(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._comms_dir = tempfile.mkdtemp()
        cls._s = top.Service(comms_dir=cls._comms_dir)

    def test_init(self):
        """Initialise a Service object.
        """
        msg = 'Object is not a top.Service'
        self.assertIsInstance(self._s, top.Service, msg)

    def test_flag_comms_previous_no_comms_files(self):
        """Check if comms flag has been set previously.
        """
        comms_flags = [os.path.join(self._comms_dir, 'sms.1.body'),
                       os.path.join(self._comms_dir, 'email.2.body.err')]
        for f in comms_flags:
            fh = open(f, 'w')
            fh.close()

        action = 'email'
        id = 1
        service = 'body'
        received = self._s.flag_comms_previous(action, id, service)
        msg = 'Previous comms flag should not exist and return False'
        self.assertFalse(received, msg)

        action = 'sms'
        id = 1
        service = 'body'
        received = self._s.flag_comms_previous(action, id, service)
        msg = 'Previous comms flag exists and return True'
        self.assertTrue(received, msg)

        action = 'email'
        id = 2
        service = 'body'
        received = self._s.flag_comms_previous(action, id, service)
        msg = 'Previous comms err flag should exist and return True'
        self.assertTrue(received, msg)

        # Clean up.
        remove_files(comms_flags)

    @classmethod
    def tearDownClass(cls):
        cls._s = None
        del cls._s
        os.removedirs(cls._comms_dir)
        del cls._comms_dir
