import unittest2
import os

import top


class TestDeliveryPartner(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._dp = top.DeliveryPartner()
        cls._db = top.DbSession()
        cls._db.connect()

        fixture_dir = os.path.join('top', 'tests', 'fixtures')

        db = cls._db
        fixtures = [{'db': db.delivery_partner,
                     'fixture': 'delivery_partners.py'}]

        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        db.commit()

    def test_init(self):
        """Placeholder test to make sure the DeliveryPartner table is
        created.
        """
        msg = 'Object is not an top.DeliveryPartner'
        self.assertIsInstance(self._dp, top.DeliveryPartner, msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        cls._dp = None
