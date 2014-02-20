import unittest2

from nparcel.postcode import translate_postcode


class TestPostcode(unittest2.TestCase):

    def test_valid_translate_postcode_non_integer(self):
        """Translate postcode to state -- valid, range-based.
        """
        postcode = 'xxx'
        received = translate_postcode(postcode)
        expected = ''
        msg = 'Non-integer postcode translation to state failed'
        self.assertEqual(received, expected, msg)

    def test_valid_translate_postcode_range_based(self):
        """Translate postcode to state -- valid, range-based.
        """
        postcode = 2000
        received = translate_postcode(postcode)
        expected = 'NSW'
        msg = 'Valid postcode (NSW) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 4123
        received = translate_postcode(postcode)
        expected = 'QLD'
        msg = 'Valid postcode (QLD) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 9123
        received = translate_postcode(postcode)
        expected = 'QLD'
        msg = 'Valid postcode (QLD) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 5023
        received = translate_postcode(postcode)
        expected = 'SA'
        msg = 'Valid postcode (SA) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 5855
        received = translate_postcode(postcode)
        expected = 'SA'
        msg = 'Valid postcode (SA) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 6125
        received = translate_postcode(postcode)
        expected = 'WA'
        msg = 'Valid postcode (WA) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 7100
        received = translate_postcode(postcode)
        expected = 'TAS'
        msg = 'Valid postcode (TAS) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

        postcode = 900
        received = translate_postcode(postcode)
        expected = 'NT'
        msg = 'Valid postcode (NT) translation to state failed -- valid'
        self.assertEqual(received, expected, msg)

    def test_invalid_translate_postcode_range_based(self):
        """Translate postcode to state -- invalid, range-based.
        """
        postcode = -1
        received = translate_postcode(postcode)
        expected = ''
        msg = 'Invalid postcode translation to state failed -- invalid'
        self.assertEqual(received, expected, msg)

    def test_valid_translate_postcode_exception_based(self):
        """Translate postcode to state -- valid, exception-based.
        """
        postcode = 2899
        received = translate_postcode(postcode)
        expected = 'NSW'
        msg = 'Valid postcode translation to state failed -- exceptions'
        self.assertEqual(received, expected, msg)
