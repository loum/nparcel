import unittest2

from nparcel.utils import date_diff


class TestUtils(unittest2.TestCase):

    def test_date_diff(self):
        """Days between two dates.
        """
        start_dt = '2013-12-05 00:00:00'
        end_dt = '2013-12-06 12:00:00'

        received = date_diff(start_dt, end_dt)
        expected = 1
        msg = 'Normal date delta check error'
        self.assertEqual(received, expected, msg)

        # Try reversing it???
        start_dt = '2013-12-06 13:00:00'
        end_dt = '2013-12-04 00:00:00'

        received = date_diff(start_dt, end_dt)
        expected = -3
        msg = 'Reversed date delta check error'
        self.assertEqual(received, expected, msg)

        # Bad date format.
        start_dt = '2013-12-02'
        end_dt = '2013-12-04 00:00:00'

        received = date_diff(start_dt, end_dt)
        msg = 'Badly formatted date delta check error'
        self.assertIsNone(received, msg)

        # Microseconds.
        start_dt = '2013-12-02 12:00:00.123456'
        end_dt = '2013-12-04 00:00:00'

        received = date_diff(start_dt, end_dt)
        expected = 1
        msg = 'Date delta check error -- with mircoseconds'
        self.assertEqual(received, expected, msg)
