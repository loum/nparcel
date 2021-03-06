import unittest2
import datetime
import tempfile
import os
import sys
import StringIO

import top
from top.utils.files import (remove_files,
                             get_directory_files_list,
                             copy_file,
                             gen_digest_path)

# Current business_unit map:
BU = {'priority': 1,
      'fast': 2,
      'ipec': 3}


class TestExporter(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls._e = top.Exporter()
        cls._e.reset()

        cls._e.set_exporter_headers({'connote_nbr': ['REF1', 'Ref1'],
                                     'item_nbr': ['ITEM_NBR'],
                                     'pickup_ts': ['PICKUP_TIME'],
                                     'pod_name': ['PICKUP_POD'],
                                     'identity_type_id': ['IDENTITY_TYPE'],
                                     'identity_type_data': ['IDENTITY_DATA']})
        cls._e.set_exporter_defaults({'identity_type_id': '9'})

        db = cls._e.db
        # Prepare some sample data.
        fixture_dir = os.path.join('top', 'tests', 'fixtures')
        fixtures = [{'db': db.agent,
                     'fixture': 'agents.py'}]
        for i in fixtures:
            fixture_file = os.path.join(fixture_dir, i['fixture'])
            db.load_fixture(i['db'], fixture_file)

        agent_ok = 1
        agent_nok = 2
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
                 'bu_id': BU['ipec']},
                {'card_ref_nbr': 'pe ref',
                 'agent_id': agent_ok,
                 'job_ts': '%s' % cls._now,
                 'service_code': 3,
                 'bu_id': BU['fast']}]
        sql = cls._e.db.job.insert_sql(jobs[0])
        priority_job_id = cls._e.db.insert(sql=sql)
        sql = cls._e.db.job.insert_sql(jobs[1])
        fast_job_id = cls._e.db.insert(sql=sql)
        sql = cls._e.db.job.insert_sql(jobs[2])
        ipec_job_id = cls._e.db.insert(sql=sql)
        sql = cls._e.db.job.insert_sql(jobs[3])
        pe_job_id = cls._e.db.insert(sql=sql)

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
                     'extract_ts': '%s' % cls._now},
                    {'connote_nbr': 'pe_connote',
                     'item_nbr': 'fast_pe_connote_item_nbr',
                     'job_id': pe_job_id,
                     'pickup_ts': '%s' % cls._now,
                     'pod_name': 'pod_name primary_elect',
                     'identity_type_id': id_type_id,
                     'identity_type_data': 'identity pe'},
                    {'connote_nbr': 'pp_connote',
                     'item_nbr': 'pp_item_nbr',
                     'job_id': pe_job_id}]
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
        msg = 'Object is not an top.Exporter'
        self.assertIsInstance(self._e, top.Exporter, msg)

    def test_collected_sql_bu_priority(self):
        """Query table for collected items -- BU: priority.
        """
        msg = 'Priorty collection check should return results.'
        sql = self._e.db.jobitem.collected_sql(business_unit=BU['priority'])
        self._e.db(sql)

        received = []
        for row in self._e.db.rows():
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
        self.assertEqual(received, expected, msg)

    def test_collected_sql_bu_fast(self):
        """Query table for collected items -- BU: fast.
        """
        sql = self._e.db.jobitem.collected_sql(business_unit=BU['fast'])
        self._e.db(sql)

        received = []
        for row in self._e.db.rows():
            received.append(row)
        expected = [('21850121786x',
                     2,
                     '%s' % self._now,
                     'pod_name 21850121786x',
                     'identity_type description',
                     'identity 21850121786x',
                     'fast_item_nbr_001',
                     'N031',
                     'VIC'),
                    ('pe_connote',
                     5,
                     '%s' % self._now,
                     'pod_name primary_elect',
                     'identity_type description',
                     'identity pe',
                     'fast_pe_connote_item_nbr',
                     'N031',
                     'VIC')]

        msg = 'Fast sepcific exporter NOT ignoring PE error'
        self.assertListEqual(received, expected, msg)

    def test_collected_sql_bu_fast_ignore_pe(self):
        """Query table for collected items -- BU: fast.
        """
        sql = self._e.db.jobitem.collected_sql(business_unit=BU['fast'],
                                               ignore_pe=True)
        self._e.db(sql)

        received = []
        for row in self._e.db.rows():
            received.append(row)
        expected = [('21850121786x',
                     2,
                     '%s' % self._now,
                     'pod_name 21850121786x',
                     'identity_type description',
                     'identity 21850121786x',
                     'fast_item_nbr_001',
                     'N031',
                     'VIC')]

        msg = 'Fast sepcific exporter ignoring PE error'
        self.assertEqual(received, expected, msg)

    def test_cleansed_valid_date_sqlite(self):
        """Cleanse valid data -- sqlite data.
        """
        row = ('', '', '2013-07-29 12:00:00.123456', '', '', '', '', '', 'VIC')
        received = self._e._cleanse(row)
        expected = ('', '', '2013-07-29 12:00:00', '', '', '', '', '', 'VIC')
        msg = 'Cleansed valid data incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_cleansed_valid_date_mssql(self):
        """Cleanse valid data -- MSSQL data.
        """
        row = ('', '', '%s' %
               datetime.datetime(2013, 07, 29, 12, 0),
               '', '', '', '', '', 'VIC')
        received = self._e._cleanse(row)
        expected = ('', '', '%s' %
                    '2013-07-29 12:00:00',
                    '', '', '', '', '', 'VIC')
        msg = 'Cleansed valid data incorrect'
        self.assertTupleEqual(received, expected, msg)

    def test_cleansed_invalid_date(self):
        """Cleanse invalid pickup_ts data.
        """
        row = ('', '', '2013-07-29 12:00:00', '', '', '', '', '', 'NSW')
        received = self._e._cleanse(row)
        expected = ('', '', '2013-07-29 12:00:00', '', '', '', '', '', 'NSW')
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

    def test_signature_archive(self):
        """Archive signature file.
        """
        # Define the archive directory.
        archive_dir = tempfile.mkdtemp()
        self._e.set_signature_dir(self._dir)

        # Create a dummy signature files.
        dummy_files = ['11111.ps', '11111.png']
        for i in dummy_files:
            sig_file = os.path.join(self._e.signature_dir, i)
            fh = open(sig_file, 'w')
            fh.close()

        archive_control = {'ps': True,
                           'png': True}
        self._e.archive_signature_file(11111,
                                       archive_control,
                                       self._e.signature_dir,
                                       archive_dir)

        # Check that the files now exists in archive.
        digest_path = gen_digest_path('11111')
        archive_digest_path = os.path.join(archive_dir, *digest_path)
        received = get_directory_files_list(archive_digest_path)
        expected = [os.path.join(archive_digest_path, x) for x in dummy_files]
        msg = 'Signature file archive directory should succeed'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Cleanup
        self._e.reset()
        remove_files(get_directory_files_list(self._e.signature_dir))
        archive_digest_path = os.path.join(archive_dir, *digest_path)
        remove_files(get_directory_files_list(archive_digest_path))
        self._e.set_signature_dir(None)
        os.removedirs(archive_digest_path)

    def test_signature_archive_selective(self):
        """Archive signature file -- only *.ps files.
        """
        # Define the archive directory.
        archive_dir = tempfile.mkdtemp()
        self._e.set_signature_dir(self._dir)

        # Create a dummy signature files.
        dummy_files = ['22222.ps', '22222.png']
        for i in dummy_files:
            sig_file = os.path.join(self._e.signature_dir, i)
            fh = open(sig_file, 'w')
            fh.close()

        archive_control = {'ps': True,
                           'png': False}
        self._e.archive_signature_file(22222,
                                       archive_control,
                                       self._e.signature_dir,
                                       archive_dir)

        # Check that the file now exists in archive.
        digest_path = gen_digest_path('22222')
        archive_digest_path = os.path.join(archive_dir, *digest_path)
        received = get_directory_files_list(archive_digest_path)
        expected = [os.path.join(archive_digest_path, '22222.ps')]
        msg = 'Signature file archive directory should succeed -- ps only'
        self.assertListEqual(received, expected, msg)

        # Cleanup
        self._e.reset()
        remove_files(get_directory_files_list(self._e.signature_dir))
        remove_files(received)
        self._e.set_signature_dir(None)
        os.removedirs(archive_digest_path)

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
        self._e.set_staging_dir(self._dir)

        bu = 'priority'
        self._e.set_out_dir(bu)
        received = self._e.out_dir
        expected = os.path.join(self._e.staging_dir, 'priority', 'out')
        msg = 'Business unit output directory incorrect'
        self.assertEqual(received, expected, msg)

        # Cleanup.
        os.rmdir(os.path.join(self._e.staging_dir, 'priority', 'out'))
        os.rmdir(os.path.join(self._e.staging_dir, 'priority'))
        self._e.set_staging_dir(None)
        self._e.reset()

    def test_process(self):
        """End to end collected items.
        """
        # Define the staging/signature directory.
        self._e.set_signature_dir(self._dir)
        self._e.set_staging_dir(self._staging_dir)
        archive_dir = tempfile.mkdtemp()
        self._e.set_archive_dir(archive_dir)

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
        file_control = {'ps': True,
                        'png': False}
        archive_control = {'ps': True,
                           'png': True}
        valid_items = self._e.process(business_unit_id=BU.get('priority'),
                                      file_control=file_control,
                                      archive_control=archive_control)
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

        # Check the staging directory.
        staging_dir = os.path.join(self._e.staging_dir, 'priority', 'out')
        received = get_directory_files_list(staging_dir)
        staging_files = [os.path.join(staging_dir, '1.ps')] + report_files
        expected = list(staging_files)
        msg = 'Staged files list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Did we archive the files?
        digest_path = gen_digest_path('1')
        archive_digest_path = os.path.join(self._e.archive_dir,
                                           *digest_path)
        received = get_directory_files_list(archive_digest_path)
        files = ['1.ps', '1.png']
        expected = [os.path.join(archive_digest_path, x) for x in files]
        msg = 'Signature file archive directory should succeed'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._e.reset()
        remove_files(staging_files)
        os.rmdir(os.path.join(self._e.staging_dir, 'priority', 'out'))
        os.rmdir(os.path.join(self._e.staging_dir, 'priority'))
        remove_files(get_directory_files_list(archive_digest_path))
        os.removedirs(archive_digest_path)

        self._e.set_staging_dir(None)
        self._e.set_signature_dir(None)
        self._e.set_archive_dir(None)
        self._e.db.rollback()

    def test_process_no_items(self):
        """No report file created if no collected items.
        """
        bu = 'priority'

        self._e.set_staging_dir(self._dir)

        self._e.set_out_dir(business_unit=bu)
        valid_items = []
        msg = 'No items should not create a report file'
        self.assertListEqual(self._e.report(valid_items), [], msg)

        # Cleanup.
        os.rmdir(os.path.join(self._e.staging_dir, 'priority', 'out'))
        os.rmdir(os.path.join(self._e.staging_dir, 'priority'))
        self._e.set_staging_dir(None)
        self._e.reset()

    def test_header(self):
        """Default export file header generation.
        """
        self._e.set_header(['REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD'])
        msg = 'Default exporter report line not as expected'
        received = self._e.get_report_line(self._e.header)
        expected = 'REF1|JOB_KEY|PICKUP_TIME|PICKUP_POD'
        self.assertEqual(received, expected, msg)

        # Cleanup.
        self._e.set_header(None)

    def test_headers_different_ordering(self):
        """Export file header generation -- different ordering.
        """
        self._e.set_header(['REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD'])
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
        self._e.set_header(['REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD'])
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
        self._e.set_header(['REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD'])
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
        self._e.set_header(['REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD'])
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
        self._e.set_header(['REF1',
                            'JOB_KEY',
                            'PICKUP_TIME',
                            'PICKUP_POD',
                            'IDENTITY_TYPE',
                            'IDENTITY_DATA',
                            'ITEM_NBR',
                            'AGENT_ID'])

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

    def test_get_files(self):
        """Get inbound report files list.
        """
        test_file_dir = os.path.join('top', 'tests', 'files')
        dir_1 = tempfile.mkdtemp()
        dir_2 = tempfile.mkdtemp()
        files = ['VIC_VANA_REI_20131108145146.txt',
                 'VIC_VANA_REP_20131108145146.txt']
        copy_file(os.path.join(test_file_dir, files[0]),
                  os.path.join(dir_1, files[0]))
        copy_file(os.path.join(test_file_dir, files[1]),
                  os.path.join(dir_2, files[1]))
        dirs = [dir_1, dir_2]
        filters = ['.*_REP_\d{14}\.txt$', '.*_REI_\d{14}\.txt$']

        received = self._e.get_files(dirs, filters)
        expected = [os.path.join(dir_1, files[0]),
                    os.path.join(dir_2, files[1])]
        msg = 'Exporter report files list error'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        for d in dirs:
            remove_files(get_directory_files_list(d))
            os.removedirs(d)

    def test_get_files_no_dirs(self):
        """Get inbound report files list -- no dirs.
        """
        dirs = []
        filters = ['.*_REP_\d{14}\.txt$', '.*_REI_\d{14}\.txt$']

        received = self._e.get_files(dirs, filters)
        expected = []
        msg = 'Exporter report files list error -- no dirs'
        self.assertListEqual(received, expected, msg)

    def test_get_files_no_filters(self):
        """Get inbound report files list - no filters.
        """
        test_file_dir = os.path.join('top', 'tests', 'files')
        dir_1 = tempfile.mkdtemp()
        dir_2 = tempfile.mkdtemp()
        files = ['VIC_VANA_REI_20131108145146.txt',
                 'VIC_VANA_REP_20131108145146.txt']
        copy_file(os.path.join(test_file_dir, files[0]),
                  os.path.join(dir_1, files[0]))
        copy_file(os.path.join(test_file_dir, files[1]),
                  os.path.join(dir_2, files[1]))
        dirs = [dir_1, dir_2]
        filters = []

        received = self._e.get_files(dirs, filters)
        expected = []
        msg = 'Exporter report files list error -- no filters'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        for d in dirs:
            remove_files(get_directory_files_list(d))
            os.removedirs(d)

    def test_parse_report_file(self):
        """Extract connote/item number from report file.
        """
        test_file_dir = os.path.join('top', 'tests', 'files')
        file = 'VIC_VANA_REI_20131108145146.txt'

        received = self._e.parse_report_file(os.path.join(test_file_dir,
                                                          file))
        expected = [{'identity_type_id': 9,
                     'identity_type_data': 'a1234',
                     'item_nbr': '6827668473420000130001',
                     'pod_name': 'Test Line1',
                     'pickup_ts': '2013-11-08 14:50:11',
                     'connote_nbr': '8473420000130'},
                    {'identity_type_id': 9,
                     'identity_type_data': 'b1234',
                     'item_nbr': '6827668473420000131001',
                     'pod_name': 'Test Line2',
                     'pickup_ts': '2013-11-08 14:50:42',
                     'connote_nbr': '8473420000131'},
                    {'identity_type_id': 9,
                     'identity_type_data': 'c1234',
                     'item_nbr': '6827668473420000131002',
                     'pod_name': 'Test Line3',
                     'pickup_ts': '2013-11-08 14:50:42',
                     'connote_nbr': '8473420000131'},
                    {'identity_type_id': 9,
                     'identity_type_data': 'd1234',
                     'item_nbr': '6827668473420000131003',
                     'pod_name': 'Test Line4',
                     'pickup_ts': '2013-11-08 14:50:42',
                     'connote_nbr': '8473420000131'}]
        msg = 'Exporter report files parsed values error'
        self.assertListEqual(received, expected, msg)

    def test_parse_report_file_parcelpoint_ref1(self):
        """Extract connote/item number from report file - PP Ref1.
        """
        test_file_dir = os.path.join('top', 'tests', 'files')
        file = 'VIC_VANA_REI_20131108145147.txt'

        received = self._e.parse_report_file(os.path.join(test_file_dir,
                                                          file))
        expected = [{'identity_type_id': 9,
                     'identity_type_data': 'a1234',
                     'item_nbr': '6827668473420000130001',
                     'pod_name': 'Test Line1',
                     'pickup_ts': '2013-11-08 14:50:11',
                     'connote_nbr': '8473420000130'}]
        msg = 'Exporter report files parsed values error - ParcelPoint Ref1'
        self.assertListEqual(received, expected, msg)

    def test_parse_missing_report_file(self):
        """Extract connote/item number from missing report file.
        """
        file_fh = tempfile.NamedTemporaryFile()
        file = file_fh.name
        file_fh.close()

        received = self._e.parse_report_file(file)
        expected = []
        msg = 'Exporter report files parsed (missing file) error'
        self.assertListEqual(received, expected, msg)

    def test_file_based_updates(self):
        """Verify file-based records are closed off.
        """
        connote = 'pe_connote'
        item_nbr = 'pe_item_nbr'

        old_exporter_dirs = self._e.exporter_dirs
        old_exporter_file_formats = self._e.exporter_file_formats

        test_file_dir = os.path.join('top', 'tests', 'files')
        dir = tempfile.mkdtemp()
        file = 'VIC_VANA_REP_20140214120000.txt'
        copy_file(os.path.join(test_file_dir, file),
                  os.path.join(dir, file))
        filters = [file]

        self._e.set_exporter_dirs([dir])
        self._e.set_exporter_file_formats(filters)

        self._e.file_based_updates(dry=False)

        # Verify update.
        sql = """SELECT connote_nbr,
       item_nbr,
       identity_type_data,
       identity_type_id,
       pickup_ts,
       pod_name
FROM job_item
WHERE connote_nbr='pp_connote' AND item_nbr = 'pp_item_nbr'"""
        self._e.db(sql)
        received = list(self._e.db.rows())
        expected = [('pp_connote',
                     'pp_item_nbr',
                     '0602',
                     9,
                     '2013-11-08 14:47:25',
                     'Tester')]
        msg = 'File-based record closure update error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        self._e.set_exporter_dirs(old_exporter_dirs)
        self._e.set_exporter_file_formats(old_exporter_file_formats)
        remove_files(get_directory_files_list(dir))
        os.removedirs(dir)
        self._e.db.rollback()

    @classmethod
    def tearDownClass(cls):
        cls._e = None
        os.removedirs(cls._dir)
        os.removedirs(cls._staging_dir)
