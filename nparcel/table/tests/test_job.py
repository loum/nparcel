import unittest2
import datetime

import nparcel


class TestJob(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._job = nparcel.Job()
        cls._db = nparcel.DbSession()
        cls._db.connect()
        cls._job_ts = datetime.datetime.now().isoformat(' ')[:-3]

    def test_check_barcode(self):
        """Bar code check.
        """
        bc = '4156778061'
        fields = {'card_ref_nbr': bc,
                  'job_ts': self._job_ts}
        sql = """
INSERT INTO job (card_ref_nbr, job_ts)
VALUES ("%s", "%s")""" % (bc, self._job_ts)
        self._db(sql)

        self._db(self._job.check_barcode(barcode=bc))
        received = []
        for row in self._db.rows():
            received.append(row[0])
        expected = [1]
        msg = 'Barcode value not returned from "job" table'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._db.connection.rollback()

    def test_job_table_insert_with_valid_nparcel_data(self):
        """Insert valid Nparcel data.
        """
        kwargs = {'address_1': '31 Bridge st,',
                  'address_2': 'Lane Cove,',
                  'agent_id': 'N031',
                  'bu_id': 1,
                  'card_ref_nbr': '4156536111',
                  'job_ts': self._job_ts,
                  'status': 1,
                  'suburb': 'Australia Other'}
        self._db(self._job.insert_sql(kwargs))

        # Cleanup.
        self._db.connection.rollback()

    def test_connote_based_job_sql(self):
        """Verify the connote_based_job_sql string.
        """
        kwargs = {'address_1': '31 Bridge st,',
                  'address_2': 'Lane Cove,',
                  'agent_id': 'N031',
                  'bu_id': 1,
                  'card_ref_nbr': '4156536111',
                  'job_ts': '%s' %
                  (datetime.datetime.now() - datetime.timedelta(seconds=99)),
                  'status': 1,
                  'suburb': 'Australia Other'}
        job_id_old = self._db.insert(self._job.insert_sql(kwargs))

        kwargs = {'address_1': '31 Bridge st,',
                  'address_2': 'Lane Cove,',
                  'agent_id': 'N031',
                  'bu_id': 1,
                  'card_ref_nbr': '4156536111',
                  'job_ts': self._job_ts,
                  'status': 1,
                  'suburb': 'Australia Other'}
        job_id = self._db.insert(self._job.insert_sql(kwargs))

        kwargs = {'address_1': '32 Banana st,',
                  'address_2': 'Banana Cove,',
                  'agent_id': 'N031',
                  'bu_id': 1,
                  'card_ref_nbr': '4156536112',
                  'job_ts': self._job_ts,
                  'status': 1,
                  'suburb': 'Australia Other'}
        dodgy_job_id = self._db.insert(self._job.insert_sql(kwargs))

        # "job_items" table.
        jobitems = [{'connote_nbr': '218501217863',
                     'job_id': job_id,
                     'pickup_ts': self._job_ts,
                     'pod_name': 'pod_name 218501217863'},
                    {'connote_nbr': '218501217863',
                     'job_id': job_id_old,
                     'pickup_ts': self._job_ts,
                     'pod_name': 'pod_name 218501217863'},
                    {'connote_nbr': '111111111111',
                     'job_id': dodgy_job_id,
                     'pickup_ts': self._job_ts,
                     'pod_name': 'pod_name 111111111111'}]
        for jobitem in jobitems:
            sql = self._db.jobitem.insert_sql(jobitem)
            self._db(sql=sql)

        sql = self._db.job.connote_based_job_sql(connote='218501217863')
        self._db(sql)
        received = []
        for row in self._db.rows():
            received.append(row[0])
        msg = 'Connote based job id query results not as expected'
        self.assertEqual(received[0], job_id, msg)

        # Cleanup.
        self._db.connection.rollback()

    def test_item_nbr_based_job_sql(self):
        """Verify the item_nbr_based_job_sql string.
        """
        now = datetime.datetime.now()
        delay = datetime.timedelta(seconds=99)
        job_kwargs = {'address_1': '31 Bridge st,',
                      'address_2': 'Lane Cove,',
                      'agent_id': 'N031',
                      'bu_id': 1,
                      'card_ref_nbr': '4156536111',
                      'job_ts': '%s' % (now - delay),
                      'status': 1,
                      'suburb': 'Australia Other'}
        job_id_old = self._db.insert(self._job.insert_sql(job_kwargs))

        job_kwargs = {'address_1': '31 Bridge st,',
                      'address_2': 'Lane Cove,',
                      'agent_id': 'N031',
                      'bu_id': 1,
                      'card_ref_nbr': '4156536111',
                      'job_ts': self._job_ts,
                      'status': 1,
                      'suburb': 'Australia Other'}
        job_id = self._db.insert(self._job.insert_sql(job_kwargs))

        job_kwargs = {'address_1': '32 Banana st,',
                      'address_2': 'Banana Cove,',
                      'agent_id': 'N031',
                      'bu_id': 1,
                      'card_ref_nbr': '4156536112',
                      'job_ts': self._job_ts,
                      'status': 1,
                      'suburb': 'Australia Other'}
        dodgy_job_id = self._db.insert(self._job.insert_sql(job_kwargs))

        # "job_items" table.
        jobitems = {'connote_nbr': '218501217863',
                    'item_nbr': 'abcdef000001',
                    'job_id': job_id,
                    'pickup_ts': self._job_ts,
                    'pod_name': 'pod_name 218501217863'},
        for jobitem in jobitems:
            sql = self._db.jobitem.insert_sql(jobitem)
            self._db(sql=sql)

        sql = self._db.job.item_nbr_based_job_sql(item_nbr='abcdef000001')
        self._db(sql)
        received = self._db.row
        expected = (job_id,)
        msg = 'Item Number based job id query results not as expected'
        self.assertEqual(received, expected, msg)

        # Cleanup.
        self._db.connection.rollback()

    def jobitem_nbr_based_job_sql(self):
        """Verify the jobitem_based_job_search_sql string.
        """
        now = datetime.datetime.now()
        delay = datetime.timedelta(seconds=99)
        job_kwargs = {'address_1': '31 Bridge st,',
                      'address_2': 'Lane Cove,',
                      'agent_id': 'N031',
                      'bu_id': 1,
                      'card_ref_nbr': '4156536111',
                      'job_ts': '%s' % (now - delay),
                      'status': 1,
                      'suburb': 'Australia Other'}
        job_id_old = self._db.insert(self._job.insert_sql(job_kwargs))

        job_kwargs = {'address_1': '31 Bridge st,',
                      'address_2': 'Lane Cove,',
                      'agent_id': 'N031',
                      'bu_id': 1,
                      'card_ref_nbr': '4156536111',
                      'job_ts': self._job_ts,
                      'status': 1,
                      'suburb': 'Australia Other'}
        job_id = self._db.insert(self._job.insert_sql(job_kwargs))

        job_kwargs = {'address_1': '32 Banana st,',
                      'address_2': 'Banana Cove,',
                      'agent_id': 'N031',
                      'bu_id': 1,
                      'card_ref_nbr': '4156536112',
                      'job_ts': self._job_ts,
                      'status': 1,
                      'suburb': 'Australia Other'}
        dodgy_job_id = self._db.insert(self._job.insert_sql(job_kwargs))

        # "job_items" table.
        jobitems = {'connote_nbr': '218501217863',
                    'item_nbr': 'abcdef000001',
                    'job_id': job_id,
                    'pickup_ts': self._job_ts,
                    'pod_name': 'pod_name 218501217863'},
        for jobitem in jobitems:
            sql = self._db.jobitem.insert_sql(jobitem)
            self._db(sql=sql)

        kwargs = {'connote': '218501217863',
                  'item_nbr': 'abcdef000001'}

        sql = self._db.job.jobitem_based_job_search_sql(**kwargs)
        self._db(sql)
        received = self._db.row
        expected = (job_id,)
        msg = 'jobitem based job id query results not as expected'
        self.assertEqual(received, expected, msg)

        # Cleanup.
        self._db.connection.rollback()

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None
        cls._job = None
        cls._job_ts = None
