import unittest2
import datetime

from top.utils.setter import (set_scalar,
                              set_date,
                              set_tuple,
                              set_list,
                              set_dict)


class Bogus(object):
    _bogus_scalar = None
    _bogus_date = None
    _bogus_tuple = ()
    _bogus_list = []
    _bogus_dict = {}

    @property
    def bogus_scalar(self):
        return self._bogus_scalar

    @set_scalar
    def set_bogus_scalar(self, value):
        pass

    @property
    def bogus_date(self):
        return self._bogus_date

    @set_date
    def set_bogus_date(self, value):
        pass

    @property
    def bogus_tuple(self):
        return self._bogus_tuple

    @set_tuple
    def set_bogus_tuple(self, value):
        pass

    @property
    def bogus_list(self):
        return self._bogus_list

    @set_list
    def set_bogus_list(self, values):
        pass

    @property
    def bogus_dict(self):
        return self._bogus_dict

    @set_dict
    def set_bogus_dict(self, values):
        pass

    @set_scalar
    def set_missing_attr(self, value):
        pass

    def __str__(self):
        return self.__class__.__name__


class TestSetter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._bogus = Bogus()

    def test_set_scalar(self):
        """Set a scalar value.
        """
        old_bogus_value = self._bogus.bogus_scalar

        value = 'Bogus Value'
        self._bogus.set_bogus_scalar(value)

        # ... and check the attribute value.
        received = self._bogus.bogus_scalar
        expected = value
        msg = 'Attribute bogus_scalar set error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        self._bogus.set_bogus_scalar(old_bogus_value)

    def test_set_date(self):
        """Set a date value.
        """
        old_bogus_value = self._bogus.bogus_date

        value = '2013-10-09 00:00:00'
        self._bogus.set_bogus_date(value)

        # ... and check the attribute value.
        received = self._bogus.bogus_date
        expected = datetime.datetime(2013, 10, 9, 0, 0)
        msg = 'Attribute bogus_scalar set error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        self._bogus.set_bogus_date(old_bogus_value)

    def test_set_date_with_real_dt(self):
        """Set a date value (datetime object).
        """
        old_bogus_value = self._bogus.bogus_date

        value = datetime.datetime(2004, 02, 12, 0, 0)
        self._bogus.set_bogus_date(value)

        # ... and check the attribute value.
        received = self._bogus.bogus_date
        expected = datetime.datetime(2004, 02, 12, 0, 0)
        msg = 'Attribute bogus_scalar set error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        self._bogus.set_bogus_date(old_bogus_value)

    def test_set_tuple(self):
        """Set a tuple value.
        """
        old_bogus_value = self._bogus.bogus_tuple

        values = ('tuple item 1', 'tuple item 2')
        self._bogus.set_bogus_tuple(values)

        # ... and check the attribute value.
        received = self._bogus.bogus_tuple
        expected = values
        msg = 'Attribute bogus_tuple set error'
        self.assertTupleEqual(received, expected, msg)

        values = ('tuple item 3', 'tuple item 4')
        self._bogus.set_bogus_tuple(values)

        # ... and check the attribute value.
        received = self._bogus.bogus_tuple
        expected = values
        msg = 'Attribute bogus_tuple set error'
        self.assertTupleEqual(received, expected, msg)

        # Clean up.
        self._bogus.set_bogus_tuple(old_bogus_value)

    def test_set_list(self):
        """Set a list value.
        """
        old_bogus_value = self._bogus.bogus_list

        values = ['list item 1', 'list item 2']
        self._bogus.set_bogus_list(values)

        # ... and check the attribute value.
        received = self._bogus.bogus_list
        expected = values
        msg = 'Attribute bogus_scalar set error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        values = ['list item 3', 'list item 4']
        self._bogus.set_bogus_list(values)

        # ... and check the attribute value.
        received = self._bogus.bogus_list
        expected = values
        msg = 'Attribute bogus_list set error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._bogus.set_bogus_list(old_bogus_value)

    def test_set_list_with_none(self):
        """Set a list value -- None value.
        """
        old_bogus_value = self._bogus.bogus_list

        values = None
        self._bogus.set_bogus_list(values)

        # ... and check the attribute value.
        received = self._bogus.bogus_list
        expected = []
        msg = 'Attribute bogus_list (None value) set error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._bogus.set_bogus_list(old_bogus_value)

    def test_set_dict_with_none(self):
        """Set a dict value -- None value.
        """
        old_bogus_value = self._bogus.bogus_dict

        values = None
        self._bogus.set_bogus_dict(values)

        # ... and check the attribute value.
        received = self._bogus.bogus_dict
        expected = {}
        msg = 'Attribute bogus_dict (None value) set error'
        self.assertDictEqual(received, expected, msg)

        # Clean up.
        self._bogus.set_bogus_dict(old_bogus_value)

    def test_set_dict(self):
        """Set a dict value.
        """
        old_bogus_value = self._bogus.bogus_dict

        values = {'dict item 1': 1, 'dict item 2': 2}
        self._bogus.set_bogus_dict(values)

        # ... and check the attribute value.
        received = self._bogus.bogus_dict
        expected = values
        msg = 'Attribute bogus_scalar set error'
        self.assertDictEqual(received, expected, msg)

        values = {'dict item 3': 3, 'dict item 4': 4}
        self._bogus.set_bogus_dict(values)

        # ... and check the attribute value.
        received = self._bogus.bogus_dict
        expected = values
        msg = 'Attribute bogus_scalar set error'
        self.assertDictEqual(received, expected, msg)

        # Clean up.
        self._bogus.set_bogus_dict(old_bogus_value)

    def test_set_dict(self):
        """Set a dict value.
        """
        old_bogus_value = self._bogus.bogus_dict

        values = {'dict item 1': 1, 'dict item 2': 2}
        self._bogus.set_bogus_dict(values)

        # ... and check the attribute value.
        received = self._bogus.bogus_dict
        expected = values
        msg = 'Attribute bogus_scalar set error'
        self.assertDictEqual(received, expected, msg)

        values = {'dict item 3': 3, 'dict item 4': 4}
        self._bogus.set_bogus_dict(values)

        # ... and check the attribute value.
        received = self._bogus.bogus_dict
        expected = values
        msg = 'Attribute bogus_scalar set error'
        self.assertDictEqual(received, expected, msg)

        # Clean up.
        self._bogus.set_bogus_dict(old_bogus_value)

    def test_set_scalar_missing_attr(self):
        """Set a scalar value -- missing attribute.
        """
        value = 'Bogus Value'
        err_msg = "'Bogus' object has no attribute '_missing_attr'"
        self.assertRaisesRegexp(AttributeError,
                                err_msg,
                                self._bogus.set_missing_attr,
                                value)

    def test_set_scalar_non_scalar_value(self):
        """Set a scalar value -- non scalar value.
        """
        value = ['Bogus Value']
        self.assertRaisesRegexp(TypeError,
                                "\"\['Bogus Value'\]\" is not a scalar",
                                self._bogus.set_bogus_scalar,
                                value)

        # ... and check the attribute value has not changed.
        received = self._bogus.bogus_scalar
        msg = 'Attribute bogus_scalar set error'
        self.assertIsNone(received, msg)

    @classmethod
    def tearDownClass(cls):
        cls._bogus = None
