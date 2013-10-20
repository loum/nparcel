import unittest2
import datetime
import tempfile
import os
import sys
import StringIO

import nparcel
from nparcel.utils.files import remove_files

# Current business_unit map:
BU = {'priority': 1,
      'fast': 2,
      'ipec': 3}


class TestExporter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._e = nparcel.Exporter()

        # Prepare some sample data.
        # "agent" table.
        agents = [{'code': 'N031',
                   'state': 'VIC'},
                  {'code': 'BAD1',
                   'state': 'NSW'}]
        agent_ok = cls._e.db.insert(cls._e.db._agent.insert_sql(agents[0]))
        agent_nok = cls._e.db.insert(cls._e.db._agent.insert_sql(agents[1]))

        cls._now = datetime.datetime.now()
        # "job" table.
        jobs = [{'card_ref_nbr': 'priority ref',
                 'agent_id': agent_ok,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU['priority']},
                {'card_ref_nbr': 'fast ref',
                 'agent_id': agent_ok,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU['fast']},
                {'card_ref_nbr': 'ipec ref',
                 'agent_id': agent_ok,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU['ipec']}]
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
                     'item_nbr': 'priority_item_nbr_001',
                     'job_id': priority_job_id,
                     'pickup_ts': '%s' % cls._now,
                     'pod_name': 'pod_name 218501217863',
                     'identity_type_id': id_type_id,
                     'identity_type_data': 'identity 218501217863'},
                    {'connote_nbr': '21850121786x',
                     'item_nbr': 'fast_item_nbr_001',
                     'job_id': fast_job_id,
                     'pickup_ts': '%s' % cls._now,
                     'pod_name': 'pod_name 21850121786x',
                     'identity_type_id': id_type_id,
                     'identity_type_data': 'identity 21850121786x'},
                    {'connote_nbr': '218501217864',
                     'item_nbr': 'priority_item_nbr_002',
                     'job_id': priority_job_id,
                     'pickup_ts': '%s' %
                     (cls._now - datetime.timedelta(seconds=86400)),
                     'pod_name': 'pod_name 218501217864',
                     'identity_type_id': id_type_id,
                     'identity_type_data': 'identity 218501217864',
                     'extract_ts': '%s' % cls._now},
                    {'connote_nbr': '218501217865',
                     'item_nbr': 'priority_item_nbr_003',
                     'job_id': priority_job_id,
                     'pickup_ts': '%s' %
                     (cls._now - datetime.timedelta(seconds=(86400 * 2))),
                     'pod_name': 'pod_name 218501217865',
                     'identity_type_id': id_type_id,
                     'identity_type_data': 'identity 218501217865',
                     'extract_ts': '%s' % cls._now}]
        for jobitem in jobitems:
            sql = cls._e.db.jobitem.insert_sql(jobitem)
            jobitem_id = cls._e.db.insert(sql=sql)

        cls._e.db.commit()

        # Create a temporary directory structure.
        cls._dir = tempfile.mkdtemp()
        cls._staging_dir = tempfile.mkdtemp()

    def test_init(self):
        """Initialise an Exporter object.
        """
        msg = 'Object is not an nparcel.Exporter'
        self.assertIsInstance(self._e, nparcel.Exporter, msg)

    def test_collected_sql_bu_priority(self):
        """Query table for collected items -- BU: priority.
        """
        msg = 'Priorty collection check should return results.'
        sql = self._e.db.jobitem.collected_sql(business_unit=BU['priority'])
        self._e.db(sql)

        received = []
        expected = [('218501217863',
                     1,
                     '%s' % self._now,
                     'pod_name 218501217863',
                     'identity_type description',
                     'identity 218501217863',
                     'priority_item_nbr_001',
                     'N031',
                     'VIC')]
        for row in self._e.db.rows():
            received.append(row)
        self.assertEqual(received, expected, msg)

    def test_collected_sql_bu_fast(self):
        """Query table for collected items -- BU: fast.
        """
        msg = 'Default collection check should return results.'
        sql = self._e.db.jobitem.collected_sql(business_unit=BU['fast'])
        self._e.db(sql)

        received = []
        expected = [('21850121786x',
                     2,
                     '%s' % self._now,
                     'pod_name 21850121786x',
                     'identity_type description',
                     'identity 21850121786x',
                     'fast_item_nbr_001',
                     'N031',
                     'VIC')]
        for row in self._e.db.rows():
            received.append(row)

        # We should have at least one seeded result so we shouldn't
        # receive an empty list.
        self.assertEqual(received, expected, msg)

    def test_cleansed_valid_date_sqlite(self):
        """Cleanse valid data -- sqlite data.
        """
        row = ('', '', '2013-07-29 12:00:00.123456', '', '', '')
        received = self._e._cleanse(row)
        expected = ('', '', '2013-07-29 12:00:00', '', '', '')
        msg = 'Cleansed valid data incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_cleansed_valid_date_mssql(self):
        """Cleanse valid data -- MSSQL data.
        """
        row = ('', '', datetime.datetime(2013, 07, 29, 12, 0), '', '', '')
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
        fh = self._e.outfile(staging, identifier='P')
        self.assertIsNotNone(fh, msg)

        outfile = fh.name
        fh.close()

        # Cleanup.
        self._e.reset()
        remove_files(outfile)
        os.rmdir(staging)

    def test_staging_file_move(self):
        """Move signature file.
        """
        # Define the staging directory.
        self._e.set_signature_dir(self._dir)

        # Create a dummy signature file.
        sig_file = os.path.join(self._dir, '1.ps')
        fh = open(sig_file, 'w')
        fh.close()

        msg = 'Signature file move should return True'
        received = self._e.move_signature_file(id=1,
                                               out_dir=self._staging_dir)
        self.assertTrue(received, msg)

        # Check that the file now exists in staging.
        msg = 'Signature file move to directory should succeed'
        staging_sig_file = os.path.join(self._staging_dir, '1.ps')
        self.assertTrue(os.path.exists(staging_sig_file), msg)

        # Cleanup
        self._e.reset()
        self._e.set_signature_dir(value=None)
        remove_files(staging_sig_file)

    def test_update_status(self):
        """Update the collected item extract_ts.
        """
        self._e._update_status(1)

        # Cleanup.
        self._e.reset()
        sql = """UPDATE job_item
SET extract_ts = null
WHERE id = 1"""
        self._e.db(sql)

    def test_set_out_directory(self):
        """Create buinsess unit output directory.
        """
        # Set the staging directory.
        self._e.set_staging_dir(value=self._dir)

        bu = 'priority'
        self._e.set_out_dir(bu)
        received = self._e.out_dir
        expected = os.path.join(self._e.staging_dir, 'priority', 'out')
        msg = 'Business unit output directory incorrect'
        self.assertEqual(received, expected, msg)

        # Cleanup.
        os.rmdir(os.path.join(self._e.staging_dir, 'priority', 'out'))
        os.rmdir(os.path.join(self._e.staging_dir, 'priority'))
        self._e.set_staging_dir(value=None)
        self._e.reset()

    def test_process(self):
        """End to end collected items.
        """
        # Define the staging/signature directory.
        self._e.set_signature_dir(self._dir)
        self._e.set_staging_dir(self._staging_dir)

        # Prepare the signature files.
        bu = 'priority'
        sql = self._e.db.jobitem.collected_sql(business_unit=BU.get(bu))
        self._e.db(sql)
        items = []
        png_files = []
        for row in self._e.db.rows():
            items.append(row)
            fh = open(os.path.join(self._e.signature_dir,
                                   '%s.ps' % str(row[1])), 'w')
            fh.close()
            fh = open(os.path.join(self._e.signature_dir,
                                   '%s.png' % str(row[1])), 'w')
            png_files.append(fh.name)
            fh.close()

        # Check if we can source a staging directory.
        self._e.set_out_dir(business_unit=bu)
        valid_items = self._e.process(business_unit_id=BU.get('priority'))
        sequence = '0, 1, 2, 3, 4, 5'
        # Returns a list, but should only get one file in this instance.
        report_files = self._e.report(valid_items, sequence=sequence)

        # Check the contents of the report file.
        fh = open(report_files[0])
        received = fh.read()
        fh.close()
        expected = ('%s|%s|%s|%s|%s|%s\n%s|%s|%s|%s|%s|%s\n' %
                    ('REF1',
                     'JOB_KEY',
                     'PICKUP_TIME',
                     'PICKUP_POD',
                     'IDENTITY_TYPE',
                     'IDENTITY_DATA',
                     '218501217863',
                     '1',
                     self._now.isoformat(' ')[:-7],
                     'pod_name 218501217863',
                     'identity_type description',
                     'identity 218501217863'))
        msg = 'Contents of Priority-based POD report file not as expected'
        self.assertEqual(received, expected, msg)

        # Clean.
        self._e.reset()
        remove_files(report_files)

        # Remove signature files.
        for item in items:
            sig_file = os.path.join(self._e._staging_dir,
                                    'priority',
                                    'out',
                                    '%s.ps' % str(item[1]))
            remove_files(sig_file)

        remove_files(png_files)
        os.rmdir(os.path.join(self._e.staging_dir, 'priority', 'out'))
        os.rmdir(os.path.join(self._e.staging_dir, 'priority'))
        self._e.set_staging_dir(value=None)
        self._e.set_signature_dir(value=None)
        self._e.db.rollback()

    def test_process_no_items(self):
        """No report file created if no collected items.
        """
        bu = 'priority'

        self._e.set_staging_dir(value=self._dir)

        self._e.set_out_dir(business_unit=bu)
        valid_items = []
        msg = 'No items should not create a report file'
        self.assertListEqual(self._e.report(valid_items), [], msg)

        # Cleanup.
        os.rmdir(os.path.join(self._e.staging_dir, 'priority', 'out'))
        os.rmdir(os.path.join(self._e.staging_dir, 'priority'))
        self._e.set_staging_dir(value=None)
        self._e.reset()

    def test_header(self):
        """Default export file header generation.
        """
        self._e.set_header(('REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD'))
        msg = 'Default exporter report line not as expected'
        received = self._e.get_report_line(self._e.header)
        expected = 'REF1|JOB_KEY|PICKUP_TIME|PICKUP_POD'
        self.assertEqual(received, expected, msg)

        # Cleanup.
        self._e.set_header(None)

    def test_headers_different_ordering(self):
        """Export file header generation -- different ordering.
        """
        self._e.set_header(('REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD'))
        msg = 'Exporter report line with modified ordering not as expected'
        received = self._e.get_report_line(self._e.header,
                                           sequence=(0, 3, 1, 2))
        expected = 'REF1|PICKUP_POD|JOB_KEY|PICKUP_TIME'
        self.assertEqual(received, expected, msg)

        # Cleanup.
        self._e.set_header(None)

    def test_headers_limited_columns(self):
        """Export file report line generation -- limited columns.
        """
        self._e.set_header(('REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD'))
        msg = 'Exporter report line with limited columns not as expected'
        received = self._e.get_report_line(self._e.header,
                                           sequence=(0, 3, 1))
        expected = 'REF1|PICKUP_POD|JOB_KEY'
        self.assertEqual(received, expected, msg)

        # Cleanup.
        self._e.set_header(None)

    def test_headers_index_out_of_range(self):
        """Export file header generation -- index out of range.
        """
        self._e.set_header(('REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD'))
        msg = 'Exporter report line with index out of range not as expected'
        received = self._e.get_report_line(self._e.header,
                                           sequence=(0, 1, 2, 3, 4))
        expected = 'REF1|JOB_KEY|PICKUP_TIME|PICKUP_POD'
        self.assertEqual(received, expected, msg)

        # Cleanup.
        self._e.set_header(None)

    def test_report_line(self):
        """Default report line entry generation.
        """
        line = ('218501217863',
                1,
                '%s' % self._now,
                'pod_name 218501217863',
                'License',
                '1234',
                'priority_item_nbr_001')
        msg = 'Default exporter line entry not as expected'
        received = self._e.get_report_line(line)
        expected = """%s|%s|%s|%s|%s|%s|%s""" % ('218501217863',
                                                 '1',
                                                 self._now,
                                                 'pod_name 218501217863',
                                                 'License',
                                                 '1234',
                                                 'priority_item_nbr_001')
        self.assertEqual(received, expected, msg)

    def test_sort(self):
        """Sort the report.
        """
        self._e.set_header(('REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD'))
        items = [('2185012178aa',
                  '10',
                  self._now,
                  'pod_name 2185012178aa'),
                 ('2185012178bb',
                  '3',
                  self._now,
                  'pod_name 2185012178bb'),
                 ('2185012178cc',
                  '1',
                  self._now,
                  'pod_name 2185012178cc')]

        stdout = sys.stdout
        sys.stdout = received = StringIO.StringIO()
        report_file = self._e.report(items)
        sys.stdout = stdout

        expected = ("""%s\n%s\n%s\n%s\n""" %
                    ('REF1|JOB_KEY|PICKUP_TIME|PICKUP_POD',
                     '2185012178cc|1|%s|pod_name 2185012178cc' % self._now,
                     '2185012178bb|3|%s|pod_name 2185012178bb' % self._now,
                     '2185012178aa|10|%s|pod_name 2185012178aa' % self._now))
        msg = 'Sorted report not as expected'
        self.assertEqual(received.getvalue(), expected, msg)

        # Cleanup.
        self._e.reset()

    def test_header_column(self):
        """JOB_KEY index get.
        """
        self._e.set_header(('REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD',
                            'IDENTITY_TYPE',
                            'IDENTITY_DATA',
                            'ITEM_NBR',
                            'AGENT_ID'))

        received = self._e.get_header_column('banana')
        expected = 0
        msg = '"banana" header column index not as expected'
        self.assertEqual(received, expected, msg)

        received = self._e.get_header_column('JOB_KEY')
        expected = 1
        msg = 'JOB_KEY column index not as expected'
        self.assertEqual(received, expected, msg)

        received = self._e.get_header_column('AGENT_ID')
        expected = 7
        msg = 'AGENT_ID column index not as expected'
        self.assertEqual(received, expected, msg)

        # Ensure the headers are clean.
        self._e.reset()

    @classmethod
    def tearDownClass(cls):
        cls._e = None
        os.removedirs(cls._dir)
        os.removedirs(cls._staging_dir)
