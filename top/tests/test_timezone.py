import unittest2

from top.timezone import convert_timezone


class TestTimezone(unittest2.TestCase):

    def test_convert_timezone_invalid_state(self):
        """Convert timezones -- invalid state.
        """
        time_string = '2013-11-25 09:51:00'
        state = 'BANANA'
        received = convert_timezone(time_string, state)
        expected = time_string
        msg = 'Timezone conversion error for TZ "BANANA"'
        self.assertEqual(received, expected, msg)

    def test_convert_timezone_vic(self):
        """Convert timezones -- VIC.
        """
        time_string = '2013-11-25 09:51:00'
        state = 'VIC'
        received = convert_timezone(time_string, state)
        expected = time_string
        msg = 'Timezone conversion error for TZ "VIC"'
        self.assertEqual(received, expected, msg)

    def test_convert_timezone_wa(self):
        """Convert timezones -- WA.
        """
        time_string = '2013-11-25 13:05:10'
        state = 'WA'
        received = convert_timezone(time_string, state)
        expected = '2013-11-25 10:05:10'
        msg = 'Timezone conversion error for TZ "WA"'
        self.assertEqual(received, expected, msg)

    def test_convert_timezone_nsw(self):
        """Convert timezones -- NSW.
        """
        time_string = '2013-11-25 13:05:10'
        state = 'NSW'
        received = convert_timezone(time_string, state)
        expected = '2013-11-25 13:05:10'
        msg = 'Timezone conversion error for TZ "NSW"'
        self.assertEqual(received, expected, msg)

    def test_convert_timezone_sa(self):
        """Convert timezones -- SA.
        """
        time_string = '2013-11-25 15:15:33'
        state = 'SA'
        received = convert_timezone(time_string, state)
        expected = '2013-11-25 14:45:33'
        msg = 'Timezone conversion error for TZ "SA"'
        self.assertEqual(received, expected, msg)

    def test_convert_timezone_nt(self):
        """Convert timezones -- NT.
        """
        time_string = '2013-11-25 20:25:40'
        state = 'NT'
        received = convert_timezone(time_string, state)
        expected = '2013-11-25 18:55:40'
        msg = 'Timezone conversion error for TZ "NT"'
        self.assertEqual(received, expected, msg)

    def test_convert_timezone_qld(self):
        """Convert timezones -- QLD.
        """
        time_string = '2013-11-25 10:25:40'
        state = 'QLD'
        received = convert_timezone(time_string, state)
        expected = '2013-11-25 09:25:40'
        msg = 'Timezone conversion error for TZ "QLD"'
        self.assertEqual(received, expected, msg)

    def test_convert_timezone_act(self):
        """Convert timezones -- ACT.
        """
        time_string = '2013-11-25 07:25:40'
        state = 'ACT'
        received = convert_timezone(time_string, state)
        expected = '2013-11-25 07:25:40'
        msg = 'Timezone conversion error for TZ "ACT"'
        self.assertEqual(received, expected, msg)

    def test_convert_timezone_tas(self):
        """Convert timezones -- TAS.
        """
        time_string = '2013-11-25 12:45:10'
        state = 'TAS'
        received = convert_timezone(time_string, state)
        expected = '2013-11-25 12:45:10'
        msg = 'Timezone conversion error for TZ "TAS"'
        self.assertEqual(received, expected, msg)
