import unittest2
import tempfile
import os

import nparcel


class TestComms(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        conf = nparcel.B2CConfig()
        conf.set_config_file('nparcel/conf/nparceld.conf')
        conf.parse_config()
        proxy = conf.proxy_string()
        cls._comms_dir = tempfile.mkdtemp()
        cls._c = nparcel.Comms(proxy=proxy,
                               scheme=conf.proxy_scheme,
                               sms_api=conf.sms_api_kwargs,
                               email_api=conf.email_api_kwargs,
                               comms_dir=cls._comms_dir)
        cls._c.set_template_base('nparcel')

    def test_init(self):
        """Initialise a Comms object.
        """
        msg = 'Object is not a nparcel.Comms'
        self.assertIsInstance(self._c, nparcel.Comms, msg)

    @classmethod
    def tearDownClass(cls):
        cls._c = None
        del cls._c
        os.removedirs(cls._comms_dir)
        del cls._comms_dir
