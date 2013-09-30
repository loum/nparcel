import unittest2
import tempfile
import os
import datetime

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
        cls._now = datetime.datetime.now()

    def test_init(self):
        """Initialise a Comms object.
        """
        msg = 'Object is not a nparcel.Comms'
        self.assertIsInstance(self._c, nparcel.Comms, msg)

    def test_send_sms(self):
        """Send reminder SMS.
        """
        date = self._c.get_return_date(self._now)
        details = {'name': 'Mannum Newsagency',
                   'address': '77 Randwell Street',
                   'suburb': 'MANNUM',
                   'postcode': '5238',
                   'item_nbr': 'item_nbr_1234',
                   'phone_nbr': '0431602145',
                   'date': '%s' % date}

        received = self._c.send_sms(details,
                                    template='sms_rem',
                                    dry=True)
        msg = 'Reminder SMS send should return True'
        self.assertTrue(received)

    def test_send_sms_test(self):
        """Send test SMS.
        """
        date = self._c.get_return_date(self._now)
        details = {'phone_nbr': '0431602145'}

        received = self._c.send_sms(details,
                                    template='sms_test',
                                    dry=True)
        msg = 'Test SMS send should return True'
        self.assertTrue(received)

    def test_get_return_date_string_based(self):
        """Create the return date -- string based.
        """
        date_str = '2013-09-19 08:52:13.308266'
        received = self._c.get_return_date(date_str)
        expected = 'Friday 27 September 2013'
        msg = 'Generated returned date error -- string input'
        self.assertEqual(received, expected, msg)

    @classmethod
    def tearDownClass(cls):
        cls._c = None
        del cls._c
        os.removedirs(cls._comms_dir)
        del cls._comms_dir
        del cls._now
