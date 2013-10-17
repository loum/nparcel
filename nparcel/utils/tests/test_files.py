import unittest2

from nparcel.utils.files import load_template


class TestFiles(unittest2.TestCase):

    def test_load_template(self):
        """Load template.
        """
        received = load_template(template='test_template.t',
                                 base_dir='nparcel/utils/tests',
                                 replace='REPLACED')
        expected = 'Test Template REPLACED'
        msg = 'Template load error'
        self.assertEqual(received.rstrip(), expected, msg)
