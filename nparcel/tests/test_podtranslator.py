import unittest2

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


    @classmethod
    def tearDownClass(cls):
        del cls._pt
