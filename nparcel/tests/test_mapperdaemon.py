import unittest2

import nparcel


class TestMapperDaemon(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._md = nparcel.MapperDaemon(pidfile=None,
                                       config='nparcel/conf/nparceld.conf')

    def test_init(self):
        """Intialise a MapperDaemon object.
        """
        msg = 'Not a nparcel.MapperDaemon object'
        self.assertIsInstance(self._md, nparcel.MapperDaemon, msg)

    def test_start(self):
        """MapperDaemon _start processing loop.
        """
        self._md.set_dry()
        self._md._start(self._md.exit_event)

    @classmethod
    def tearDownClass(cls):
        cls._md = None
        del cls._md
