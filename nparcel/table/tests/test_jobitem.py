import unittest2
import datetime

import nparcel

# Current busness_unit map:
BU = {'priority': 1,
      'fast': 2,
      'ipec': 3}


class TestJobItem(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._job_item = nparcel.JobItem()
        cls._db = nparcel.DbSession()
        cls._db.connect()

        # Prepare some sample data.
        # Agent.
        agents = [{'code': 'N031',
                   'state': 'VIC',
                   'name': 'N031 Name',
                   'address': 'N031 Address',
                   'postcode': '1234',
                   'suburb': 'N031 Suburb'},
                  {'code': 'BAD1',
                   'state': 'NSW',
                   'name': 'BAD1 Name',
                   'address': 'BAD1 Address',
                   'postcode': '5678',
                   'suburb': 'BAD1 Suburb'}]
        agent_ok = cls._db.insert(cls._db._agent.insert_sql(agents[0]))
        agent_nok = cls._db.insert(cls._db._agent.insert_sql(agents[1]))

        cls._now = datetime.datetime.now()
        # "job" table
        jobs = [{'card_ref_nbr': 'priority ref',
                 'agent_id': agent_ok,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU['priority']}]
        sql = cls._db.job.insert_sql(jobs[0])
        priority_job_id = cls._db.insert(sql=sql)

        # "identity_type" table.
        identity_types = [{'description': 'identity_type description'}]
        for identity_type in identity_types:
            sql = cls._db.identity_type.insert_sql(identity_type)
            id_type_id = cls._db.insert(sql=sql)

        # "job_item" table.
        jobitems = [{'connote_nbr': '218501217863',
                     'item_nbr': 'priority_item_nbr_001',
                     'job_id': priority_job_id,
                     'created_ts': '%s' % cls._now,
                     'pickup_ts': '%s' % cls._now,
                     'pod_name': 'pod_name 218501217863',
                     'identity_type_id': id_type_id,
                     'identity_type_data': 'identity 218501217863',
                     'email_addr': 'loumar@tollgroup.com',
                     'phone_nbr': '0431602145'},
                    {'connote_nbr': '218501217old',
                     'item_nbr': 'priority_item_nbr_old',
                     'job_id': priority_job_id,
                     'created_ts': '%s' %
                      (cls._now - datetime.timedelta(seconds=864000)),
                     'pod_name': 'pod_name 218501217old',
                     'identity_type_id': id_type_id,
                     'identity_type_data': 'identity 218501217old',
                     'email_addr': 'loumar@tollgroup.com'}]
        sql = cls._db.jobitem.insert_sql(jobitems[0])
        cls._valid_job_item_id_01 = cls._db.insert(sql=sql)
        sql = cls._db.jobitem.insert_sql(jobitems[1])
        cls._valid_job_item_id_02 = cls._db.insert(sql=sql)

        cls._db.commit()

    def test_init(self):
        """Initialise a JobItem object.
        """
        msg = "Object is not an nparcel.JobItem"
        self.assertIsInstance(self._job_item, nparcel.JobItem, msg)

    def test_jobitem_table_insert_with_valid_nparcel_data(self):
        """Insert valid Nparcel data into "job_item" table.
        """
        kwargs = {'connote_nbr': '2185012insert',
                  'consumer_name': 'Diane Donohoe',
                  'pieces': '00001',
                  'status': 1,
                  'created_ts': datetime.datetime.now().isoformat(' ')[:-3]}
        received = self._db.insert(self._job_item.insert_sql(kwargs))
        msg = '"job_item" table insert should return integer value'
        self.assertTrue(isinstance(received, int), msg)

        self._db.connection.rollback()

    def test_connote_sql(self):
        """Verify the connote_sql string.
        """
        connote = '218501217899'

        # Seed the table with sample data.
        kwargs = {'connote_nbr': connote,
                  'status': 1,
                  'created_ts': datetime.datetime.now().isoformat(' ')[:-3]}
        id = self._db.insert(self._job_item.insert_sql(kwargs))

        # Check the query via SQL.
        sql = self._db.jobitem.connote_sql(connote=connote)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row[0])
        expected = [id]
        msg = 'job_item.connote return value not as expected'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._db.connection.rollback()

    def test_connote_item_nbr_sql(self):
        """Verify the connote_item_nbr_sql string.
        """
        connote = '218501217nbr'
        item_nbr = 'abcdef000001'

        # Seed the table with sample data.
        kwargs = {'connote_nbr': connote,
                  'item_nbr': item_nbr,
                  'status': 1,
                  'created_ts': datetime.datetime.now().isoformat(' ')[:-3]}
        id = self._db.insert(self._job_item.insert_sql(kwargs))

        # Check the query via SQL.
        sql = self._db.jobitem.connote_item_nbr_sql(connote=connote,
                                                    item_nbr=item_nbr)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row[0])
        expected = [id]
        msg = 'job_item serch return value not as expected'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._db.connection.rollback()

    def test_item_nbr_sql(self):
        """Verify the item_number_sql string.
        """
        item_nbr = 'abcdef012345'

        # Seed the table with sample data.
        kwargs = {'item_nbr': item_nbr,
                  'status': 1,
                  'created_ts': datetime.datetime.now().isoformat(' ')[:-3]}
        id = self._db.insert(self._job_item.insert_sql(kwargs))

        # Check the query via SQL.
        sql = self._db.jobitem.item_number_sql(item_nbr=item_nbr)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row[0])
        expected = [id]
        msg = 'job_item.item_nbr return value not as expected'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._db.connection.rollback()

    def test_collected_sql(self):
        """Verify the collected_sql SQL string.
        """
        sql = self._db.jobitem.collected_sql(business_unit=1)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [('218501217863',
                     1,
                     '%s' % self._now,
                     'pod_name 218501217863',
                     'identity_type description',
                     'identity 218501217863',
                     'priority_item_nbr_001',
                     'N031',
                     'VIC')]
        msg = 'collected_sql SQL query did not return expected result'
        self.assertListEqual(received, expected)

    def test_reminder_sql(self):
        """Verify the uncollected_sql SQL string.
        """
        start_time = self._now - datetime.timedelta(seconds=(86400 * 11))
        old_time = self._now - datetime.timedelta(seconds=(86400 * 4))
        sql = self._db.jobitem.uncollected_sql(start_time, old_time)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [(self._valid_job_item_id_02,)]
        msg = 'uncollected_sql SQL query did not return expected result'
        self.assertListEqual(received, expected)

    def test_job_item_agent_details_sql(self):
        """Verify the job_item_agent_details_sql SQL string.
        """
        job_item_id = self._valid_job_item_id_01
        sql = self._db.jobitem.job_item_agent_details_sql(job_item_id)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [('N031 Name',
                     'N031 Address',
                     'N031 Suburb',
                     '1234',
                     '218501217863',
                     'priority_item_nbr_001',
                     self._now.isoformat(' '),
                     'loumar@tollgroup.com',
                     '0431602145')]
        msg = 'Agent details based on job_item.id not as expected'
        self.assertListEqual(received, expected, msg)

    def test_update_reminder_ts_sql(self):
        """Verify the update_reminder_ts SQL string.
        """
        job_item_id = self._valid_job_item_id_01
        sql = self._db.jobitem.update_reminder_ts_sql(job_item_id)
        self._db(sql)

        # Cleanup.
        self._db.rollback()

    @classmethod
    def tearDownClass(cls):
        cls._db.close()
        cls._db = None
        del cls._db
        del cls._valid_job_item_id_01
        del cls._valid_job_item_id_02
