import unittest2
import datetime

import nparcel


class TestPodTranslator(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._pt = nparcel.PodTranslator()

    def test_init(self):
        """Initialise an PodTranslator object.
        """
        msg = 'Object is not an nparcel.PodTranslator'
        self.assertIsInstance(self._pt, nparcel.PodTranslator, msg)

    def test_token_generator_datetime_object(self):
        """Verify the token_generator -- datetime object provided
        """
        dt = datetime.datetime(2014, 04, 07, 19, 22, 00, 123456)

        received = self._pt.token_generator(dt)
        expected = '03968625201'
        msg = 'token_generator with datetime object error'
        self.assertEqual(received, expected, msg)

        dt = datetime.datetime(2033, 05, 18, 13, 33, 19, 999999)

        received = self._pt.token_generator(dt)
        expected = '09999999999'
        msg = 'token_generator with datetime object error'
        self.assertEqual(received, expected, msg)

    def test_token_generator_datetime_object_above_threshold(self):
        """Verify the token_generator -- datetime object above threshold
        """
        dt = datetime.datetime(2033, 05, 18, 13, 33, 20, 1)

        received = self._pt.token_generator(dt)
        msg = 'token_generator with datetime above threshold error'
        self.assertIsNone(received, msg)

    def test_token_generator_current_time(self):
        """Verify the token_generator -- current_time.
        """
        received = self._pt.token_generator()
        msg = 'token_generator using current time'
        self.assertIsNotNone(received, msg)

    @classmethod
    def tearDownClass(cls):
        del cls._pt
