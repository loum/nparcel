import unittest2
import datetime
import os

import nparcel

# Current busness_unit map:
BU = {'priority': 1,
      'fast': 2,
      'ipec': 3}


class TestJobItem(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._now = datetime.datetime.now()

        cls.maxDiff = None
        cls._job_item = nparcel.JobItem()
        cls._db = nparcel.DbSession()
        cls._db.connect()

        fixture_dir = os.path.join('nparcel', 'tests', 'fixtures')
        db = cls._db
        # Prepare some sample data.
        # Agent.
        fixture_file = os.path.join(fixture_dir, 'agents.py')
        db.load_fixture(db.agent, fixture_file)

        # Job table.
        fixture_file = os.path.join(fixture_dir, 'jobs.py')
        db.load_fixture(db.job, fixture_file)
        sql = """UPDATE job
SET job_ts = '%s'""" % cls._now
        db(sql)

        # "identity_type" table.
        fixture_file = os.path.join(fixture_dir, 'identity_type.py')
        db.load_fixture(db.identity_type, fixture_file)

        # job_items table.
        fixture_file = os.path.join(fixture_dir, 'jobitems.py')
        db.load_fixture(db.jobitem, fixture_file)

        # Update the timestamps.
        sql = """UPDATE job_item
SET created_ts = '%s'
WHERE id IN (1, 3, 4, 5)""" % cls._now
        db(sql)

        sql = """UPDATE job_item
SET pickup_ts = '%s'
WHERE id IN (1, 5)""" % cls._now
        db(sql)

        delayed_dt = cls._now - datetime.timedelta(seconds=(86400 * 5))
        sql = """UPDATE job_item
SET created_ts = '%(dt)s', notify_ts = '%(dt)s'
WHERE id = 2""" % {'dt': delayed_dt}
        db(sql)

        cls._valid_job_item_id_01 = 1
        cls._valid_job_item_id_02 = 2
        cls._valid_job_item_id_03 = 3
        cls._valid_job_item_id_04 = 4
        cls._valid_job_item_id_05 = 5

        db.commit()

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
                     "Driver's License",
                     'identity 218501217863',
                     'priority_item_nbr_001',
                     'N031',
                     'VIC'),
                    ('pe_collected_connote',
                     5,
                     '%s' % self._now,
                     'pod_name pe_collected',
                     "Driver's License",
                     'identity pe_collected',
                     'pe_collected_connote',
                     'N031',
                     'VIC')]
        msg = 'collected_sql SQL query did not return expected result'
        self.assertListEqual(received, expected)

    def test_ignore_pe_collected_sql(self):
        """Verify the collected_sql SQL string.
        """
        sql = self._db.jobitem.collected_sql(business_unit=1,
                                             ignore_pe=True)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [('218501217863',
                     1,
                     '%s' % self._now,
                     'pod_name 218501217863',
                     "Driver's License",
                     'identity 218501217863',
                     'priority_item_nbr_001',
                     'N031',
                     'VIC')]
        msg = 'ignore_pe_collected_sql SQL query string error'
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
                     '0431602145',
                     self._now.isoformat(' '),
                     1)]
        msg = 'Agent details based on job_item.id not as expected'
        self.assertListEqual(received, expected, msg)

    def test_update_reminder_ts_sql(self):
        """Verify the update_reminder_ts SQL string.
        """
        job_item_id = self._valid_job_item_id_01

        sql = """SELECT id
FROM job_item
WHERE id = %d
AND reminder_ts IS NOT NULL""" % job_item_id
        self._db(sql)
        received = []
        for row in self._db.rows():
            received.append(row)
        expected = []
        msg = 'job_item list should be empty before reminder_ts update'
        self.assertListEqual(received, expected, msg)

        sql = self._db.jobitem.update_reminder_ts_sql(job_item_id)
        self._db(sql)

        sql = """SELECT id
FROM job_item
WHERE id = %d
AND reminder_ts IS NOT NULL""" % job_item_id
        self._db(sql)
        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [(job_item_id, )]
        msg = 'job_item list not as expected after reminder_ts update'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._db.rollback()

    def test_update_notify_ts_sql(self):
        """Verify the update_notify_ts SQL string.
        """
        job_item_id = self._valid_job_item_id_01

        sql = """SELECT id
FROM job_item
WHERE id = %d
AND notify_ts IS NOT NULL""" % job_item_id
        self._db(sql)
        received = []
        for row in self._db.rows():
            received.append(row)
        expected = []
        msg = 'job_item list should be empty before notify_ts update'
        self.assertListEqual(received, expected, msg)

        sql = self._db.jobitem.update_notify_ts_sql(job_item_id)
        self._db(sql)

        sql = """SELECT id
FROM job_item
WHERE id = %d
AND notify_ts IS NOT NULL""" % job_item_id
        self._db(sql)
        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [(job_item_id, )]
        msg = 'job_item list not as expected after notify_ts update'
        self.assertListEqual(received, expected, msg)

        # Cleanup.
        self._db.rollback()

    def test_connote_base_primary_elect_job(self):
        """Verify connote_base_primary_elect_job SQL string.
        """
        connote = 'pe_connote'
        sql = self._db.jobitem.connote_base_primary_elect_job(connote)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [(self._valid_job_item_id_03,)]
        msg = 'connote_base_primary_elect_job return list incorrect'
        self.assertListEqual(received, expected, msg)

    def test_uncollected_primary_elect_jobitems_sql(self):
        """Verify uncollected_primary_elect_jobitems SQL string.
        """
        bu_ids = (1, 2, 3)
        sql = self._db.jobitem.uncollected_jobitems_sql(bu_ids=bu_ids)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [(3, 'pe_connote', 'pe_item_nbr'),
                    (10, 'GOLW010997', 'GOLW010997'),
                    (12, 'ANWD011307', 'ANWD011307001'),
                    (13, 'IANZ012764', 'IANZ012764')]
        msg = 'uncollected_primary_elect_jobitems_sql return list incorrect'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    def test_uncollected_service_code_jobitems_sql_no_bu_ids(self):
        """Verify uncollected_service_code_jobitems SQL string.
        """
        bu_ids = ()
        service_code = 1
        sql = self._db.jobitem.uncollected_jobitems_sql(service_code,
                                                        bu_ids)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row)
        expected = []
        msg = 'Uncollected service code with no bu_ids error'
        self.assertListEqual(received, expected, msg)

    def test_uncollected_service_code_jobitems_sql_bu_1(self):
        """Verify uncollected_service_code_jobitems SQL string.
        """
        bu_ids = (1,)
        service_code = 1
        sql = self._db.jobitem.uncollected_jobitems_sql(service_code,
                                                        bu_ids)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [(6,
                     'uncollected_connote_sc_1',
                     'uncollected_connote_sc_1_item_nbr')]
        msg = 'Uncollected service code with bu_ids 1 error'
        self.assertListEqual(received, expected, msg)

    def test_uncollected_service_code_jobitems_sql_bu_2(self):
        """Verify uncollected_service_code_jobitems SQL string.
        """
        bu_ids = (1, 2)
        service_code = 4
        sql = self._db.jobitem.uncollected_jobitems_sql(service_code,
                                                        bu_ids)
        self._db(sql)

        received = []
        for row in self._db.rows():
            received.append(row)
        expected = [(9,
                     'uncollected_connote_sc_4',
                     'uncollected_connote_sc_4_item_nbr'),
                    (14, 'TWAD358893', 'TWAD358893001')]
        msg = 'Uncollected service code with bu_ids 4 error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

    @classmethod
    def tearDownClass(cls):
        cls._db.disconnect()
        cls._db = None
        del cls._db
        del cls._valid_job_item_id_01
        del cls._valid_job_item_id_02
        del cls._valid_job_item_id_03
