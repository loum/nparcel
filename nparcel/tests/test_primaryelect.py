import unittest2

import nparcel


class TestPrimaryElect(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        # Prepare our PrimaryElect object.
        conf = nparcel.B2CConfig()
        conf.set_config_file('nparcel/conf/nparceld.conf')
        conf.parse_config()
        proxy = conf.proxy_string()
        cls._r = nparcel.PrimaryElect(proxy=proxy,
                                      scheme=conf.proxy_scheme,
                                      sms_api=conf.sms_api_kwargs,
                                      email_api=conf.email_api_kwargs)
        cls._r.set_template_base('nparcel')

    def test_init(self):
        """Initialise a PrimaryElect object.
        """
        msg = 'Object is not a nparcel.PrimaryElect'
        self.assertIsInstance(self._r, nparcel.PrimaryElect, msg)

    @classmethod
    def tearDownClass(cls):
        cls._r = None
        del cls._r
