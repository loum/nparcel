import unittest2
import datetime
import tempfile
import os

import nparcel

# Current busness_unit map:
BU = {'Priority': 1,
      'Fast': 2,
      'Ipec': 3}


class TestExporter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._e = nparcel.Exporter()

        now = datetime.datetime.now()
        # "job" table
        jobs = [{'card_ref_nbr': 'Priority ref',
                 'job_ts': '%s' % now,
                 'bu_id': BU['Priority']},
                {'card_ref_nbr': 'Fast ref',
                 'job_ts': '%s' % now,
                 'bu_id': BU['Fast']},
                {'card_ref_nbr': 'Ipec ref',
                 'job_ts': '%s' % now,
                 'bu_id': BU['Ipec']}]
        sql = cls._e.db.job.insert_sql(jobs[0])
        priority_job_id = cls._e.db.insert(sql=sql)
        sql = cls._e.db.job.insert_sql(jobs[1])
        fast_job_id = cls._e.db.insert(sql=sql)
        sql = cls._e.db.job.insert_sql(jobs[2])
        ipec_job_id = cls._e.db.insert(sql=sql)

        # "identity_type" table.
        identity_types = [{'description': 'identity_type description'}]
        for identity_type in identity_types:
            sql = cls._e.db.identity_type.insert_sql(identity_type)
            id_type_id = cls._e.db.insert(sql=sql)

        # "job_items" table.
        jobitems = [{'connote_nbr': '218501217863',
                     'job_id': priority_job_id,
                     'pickup_ts': '%s' % now,
                     'pod_name': 'pod_name 218501217863',
                     'identity_type_id': id_type_id,
                     'identity_type_data': 'identity 218501217863'},
                    {'connote_nbr': '21850121786x',
                     'job_id': fast_job_id,
                     'pickup_ts': '%s' % now,
                     'pod_name': 'pod_name 21850121786x',
                     'identity_type_id': id_type_id,
                     'identity_type_data': 'identity 21850121786x'},
                    {'connote_nbr': '218501217864',
                     'job_id': priority_job_id,
                     'pickup_ts': '%s' %
                     (now - datetime.timedelta(seconds=86400)),
                     'pod_name': 'pod_name 218501217864',
                     'identity_type_id': id_type_id,
                     'identity_type_data': 'identity 218501217864',
                     'extract_ts': '%s' % now},
                    {'connote_nbr': '218501217865',
                     'job_id': priority_job_id,
                     'pickup_ts': '%s' %
                     (now - datetime.timedelta(seconds=(86400 * 2))),
                     'pod_name': 'pod_name 218501217865',
                     'identity_type_id': id_type_id,
                     'identity_type_data': 'identity 218501217865',
                     'extract_ts': '%s' % now}]
        for jobitem in jobitems:
            sql = cls._e.db.jobitem.insert_sql(jobitem)
            jobitem_id = cls._e.db.insert(sql=sql)

        # Create a temporary directory structure.
        cls._dir = tempfile.mkdtemp()

    def test_init(self):
        """Initialise an Exporter object.
        """
        msg = 'Object is not an nparcel.Exporter'
        self.assertIsInstance(self._e, nparcel.Exporter, msg)

    def test_collected_sql_bu_priority(self):
        """Query table for collected items -- BU: Priority.
        """
        msg = 'Priorty collection check should return results.'
        sql = self._e.db.jobitem.collected_sql(business_unit=BU['Priority'])
        self._e.db(sql)

        received = []
        expected = '218501217863'
        for row in self._e.db.rows():
            received.append(row)

        # We should have at least one seeded result so we shouldn't
        # receive an empty list.
        self.assertEqual(received[0][0], expected, msg)

    def test_collected_sql_bu_fast(self):
        """Query table for collected items -- BU: Fast.
        """
        msg = 'Default collection check should return results.'
        sql = self._e.db.jobitem.collected_sql(business_unit=BU['Fast'])
        self._e.db(sql)

        received = []
        expected = '21850121786x'
        for row in self._e.db.rows():
            received.append(row)

        # We should have at least one seeded result so we shouldn't
        # receive an empty list.
        self.assertEqual(received[0][0], expected, msg)

    def test_cached_items_if_file_not_provided(self):
        """Check cached items if a cache file is not provided.
        """
        msg = "Collected items with no cache should not be None"
        self._e.get_collected_items(business_unit=1)
        self.assertIsNotNone(self._e._collected_items, msg)

    def test_report(self):
        """Verify reporter output.
        """
        # Regenerate the collected items list.
        del self._e._collected_items[:]
        self._e.get_collected_items(business_unit=1)
        self._e.report()

    def test_cleansed_valid_date(self):
        """Cleanse valid data.
        """
        row = ('', '', '2013-07-29 12:00:00.123456', '', '', '')
        received = self._e._cleanse(row)
        expected = ('', '', '2013-07-29 12:00:00', '', '', '')
        msg = 'Cleansed valid data incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_cleansed_invalid_date(self):
        """Cleanse invalid pickup_ts data.
        """
        row = ('', '', '2013-07-29 12:00:00', '', '', '')
        received = self._e._cleanse(row)
        expected = ('', '', '2013-07-29 12:00:00', '', '', '')
        msg = 'Cleansed valid data incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_output_file_creation(self):
        """Output file handle creation.
        """
        staging = os.path.join(self._dir, 'staging')

        msg = 'Export reporting file handle should not be None'
        fh = self._e.outfile(staging)
        self.assertIsNotNone(fh, msg)

        outfile = fh.name
        fh.close()

        # Cleanup.
        os.remove(outfile)
        os.rmdir(staging)

    def test_output_file_write(self):
        """Output file write.
        """
        staging = os.path.join(self._dir, 'staging')

        # Regenerate the collected items list.
        del self._e._collected_items[:]

        self._e.set_staging_dir(staging)
        self._e.get_collected_items(business_unit=1)
        file_name = self._e.report()

        # Restore and cleanup.
        os.remove(file_name.replace('.txt.tmp', '.txt'))
        os.rmdir(staging)
        self._e.set_staging_dir(None)

    @classmethod
    def tearDownClass(cls):
        cls._r = None
        os.removedirs(cls._dir)
