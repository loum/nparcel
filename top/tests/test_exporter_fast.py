import unittest2
import datetime
import tempfile
import os

import top
from top.utils.files import (get_directory_files_list,
                             remove_files,
                             gen_digest_path)
from top.timezone import convert_timezone

# Current business_unit map:
BU = {'fast': 2}


class TestExporterFast(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls._seq = '0, 1, 2, 3, 4, 5, 6'

        cls._e = top.Exporter()

        # Prepare some sample data.
        # "agent" table.
        agents = [{'code': 'AG01',
                   'state': 'VIC'},
                  {'code': 'AG02',
                   'state': 'NSW'},
                  {'code': 'AG03',
                   'state': 'QLD'},
                  {'code': 'AG04',
                   'state': 'TAS'},
                  {'code': 'AG05',
                   'state': 'SA'}]
        agent_vic = cls._e.db.insert(cls._e.db._agent.insert_sql(agents[0]))
        agent_nsw = cls._e.db.insert(cls._e.db._agent.insert_sql(agents[1]))
        agent_qld = cls._e.db.insert(cls._e.db._agent.insert_sql(agents[2]))
        agent_tas = cls._e.db.insert(cls._e.db._agent.insert_sql(agents[3]))
        agent_sa = cls._e.db.insert(cls._e.db._agent.insert_sql(agents[4]))

        cls._now = datetime.datetime.now()
        # "job" table.
        jobs = [{'card_ref_nbr': 'fast card ref 01',
                 'agent_id': agent_vic,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU.get('fast')},
                {'card_ref_nbr': 'fast card ref 02',
                 'agent_id': agent_nsw,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU.get('fast')},
                {'card_ref_nbr': 'fast card ref 03',
                 'agent_id': agent_nsw,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU.get('fast')},
                {'card_ref_nbr': 'fast card ref 04',
                 'agent_id': agent_qld,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU.get('fast')},
                {'card_ref_nbr': 'fast card ref 05',
                 'agent_id': agent_tas,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU.get('fast')},
                {'card_ref_nbr': 'fast card ref 06',
                 'agent_id': agent_sa,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU.get('fast')}]
        sql = cls._e.db.job.insert_sql(jobs[0])
        cls._job_id_01 = cls._e.db.insert(sql=sql)
        sql = cls._e.db.job.insert_sql(jobs[1])
        cls._job_id_02 = cls._e.db.insert(sql=sql)
        sql = cls._e.db.job.insert_sql(jobs[2])
        cls._job_id_03 = cls._e.db.insert(sql=sql)
        sql = cls._e.db.job.insert_sql(jobs[3])
        cls._job_id_04 = cls._e.db.insert(sql=sql)
        sql = cls._e.db.job.insert_sql(jobs[4])
        cls._job_id_05 = cls._e.db.insert(sql=sql)
        sql = cls._e.db.job.insert_sql(jobs[5])
        cls._job_id_06 = cls._e.db.insert(sql=sql)

        # "identity_type" table.
        identity_types = [{'description': 'License'},
                          {'description': 'Passport'}]
        sql = cls._e.db.identity_type.insert_sql(identity_types[0])
        cls._id_type_license = cls._e.db.insert(sql)
        sql = cls._e.db.identity_type.insert_sql(identity_types[1])
        cls._id_type_passport = cls._e.db.insert(sql)

        # "job_items" table.
        jobitems = [{'connote_nbr': 'fast_connote_nbr_01',
                     'item_nbr': 'fast_item_nbr_01',
                     'job_id': cls._job_id_01,
                     'pickup_ts': '%s' % cls._now,
                     'pod_name': 'pod_name fast 01',
                     'identity_type_id': cls._id_type_license,
                     'identity_type_data': 'fast identity 01'},
                    {'connote_nbr': 'fast_connote_nbr_02',
                     'item_nbr': 'fast_item_nbr_02',
                     'job_id': cls._job_id_02,
                     'pickup_ts': '%s' % cls._now,
                     'extract_ts': '%s' % cls._now,
                     'pod_name': 'pod_name fast 02',
                     'identity_type_id': cls._id_type_passport,
                     'identity_type_data': 'fast identity 02'},
                    {'connote_nbr': 'fast_connote_nbr_03',
                     'item_nbr': 'fast_item_nbr_03',
                     'job_id': cls._job_id_03,
                     'pickup_ts': '%s' % cls._now,
                     'pod_name': 'pod_name fast 03',
                     'identity_type_id': cls._id_type_passport,
                     'identity_type_data': 'fast identity 03'},
                    {'connote_nbr': 'fast_connote_nbr_04',
                     'item_nbr': 'fast_item_nbr_04',
                     'job_id': cls._job_id_04,
                     'pickup_ts': '%s' % cls._now,
                     'pod_name': 'pod_name fast 04',
                     'identity_type_id': cls._id_type_license,
                     'identity_type_data': 'fast identity 04'},
                    {'connote_nbr': 'fast_connote_nbr_05',
                     'item_nbr': 'fast_item_nbr_05',
                     'job_id': cls._job_id_05,
                     'pickup_ts': '%s' % cls._now,
                     'pod_name': 'pod_name fast 05',
                     'identity_type_id': cls._id_type_license,
                     'identity_type_data': 'fast identity 05'},
                    {'connote_nbr': 'fast_connote_nbr_06',
                     'item_nbr': 'fast_item_nbr_06',
                     'job_id': cls._job_id_06,
                     'pickup_ts': '%s' % cls._now,
                     'pod_name': 'pod_name fast 06',
                     'identity_type_id': cls._id_type_license,
                     'identity_type_data': 'fast identity 06'}]

        for jobitem in jobitems:
            sql = cls._e.db.jobitem.insert_sql(jobitem)
            cls._e.db.insert(sql)

        cls._e.db.commit()

        # Create a temporary directory structure.
        cls._dir = tempfile.mkdtemp()
        cls._staging_dir = tempfile.mkdtemp()
        cls._archive_dir = tempfile.mkdtemp()
        cls._e.set_archive_dir(cls._archive_dir)

    def test_header(self):
        """Fast export file header generation.
        """
        sql = self._e.db.jobitem.collected_sql(business_unit=BU.get('fast'))
        self._e.db(sql)

        # Get the query header.
        self._e.set_header(self._e.db.columns())

        received = self._e.get_report_line(line=self._e.header,
                                           sequence=self._seq)
        expected = ('%s|%s|%s|%s|%s|%s|%s' % ('REF1',
                                              'JOB_KEY',
                                              'PICKUP_TIME',
                                              'PICKUP_POD',
                                              'IDENTITY_TYPE',
                                              'IDENTITY_DATA',
                                              'ITEM_NBR'))
        msg = 'Fast Exporter report header not as expected'
        self.assertEqual(received, expected, msg)

    def test_report_line_entry(self):
        """Fast export file line entry generation.
        """
        # Extract report items from the DB.
        self._e.get_collected_items(business_unit_id=BU.get('fast'))
        received = []
        for row in self._e._collected_items:
            received.append(self._e.get_report_line(line=row,
                                                    sequence=self._seq))
        expected = (['%s|%s|%s|%s|%s|%s|%s' %
                     ('fast_connote_nbr_01',
                      '1',
                      self._now.isoformat(' ')[:-7],
                      'pod_name fast 01',
                      'License',
                      'fast identity 01',
                      'fast_item_nbr_01'),
                     '%s|%s|%s|%s|%s|%s|%s' %
                     ('fast_connote_nbr_03',
                      '3',
                      self._now.isoformat(' ')[:-7],
                      'pod_name fast 03',
                      'Passport',
                      'fast identity 03',
                      'fast_item_nbr_03'),
                     '%s|%s|%s|%s|%s|%s|%s' %
                     ('fast_connote_nbr_04',
                      '4',
                      convert_timezone(self._now.isoformat(' ')[:-7], 'QLD'),
                      'pod_name fast 04',
                      'License',
                      'fast identity 04',
                      'fast_item_nbr_04'),
                     '%s|%s|%s|%s|%s|%s|%s' %
                     ('fast_connote_nbr_05',
                      '5',
                      self._now.isoformat(' ')[:-7],
                      'pod_name fast 05',
                      'License',
                      'fast identity 05',
                      'fast_item_nbr_05'),
                     '%s|%s|%s|%s|%s|%s|%s' %
                     ('fast_connote_nbr_06',
                      '6',
                      convert_timezone(self._now.isoformat(' ')[:-7], 'SA'),
                      'pod_name fast 06',
                      'License',
                      'fast identity 06',
                      'fast_item_nbr_06')])
        msg = 'Fast Exporter report line items not as expected'
        self.assertListEqual(received, expected, msg)

    def test_process_archive_png_files(self):
        """End to end collected items -- archive png files.
        """
        # Define the staging/signature directory.
        self._e.set_signature_dir(self._dir)
        self._e.set_staging_dir(self._staging_dir)

        # Prepare the signature files.
        bu = 'fast'
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
        archive_control = {'ps': False,
                           'png': False}
        self._e.set_out_dir(business_unit='fast')
        valid_items = self._e.process(business_unit_id=BU.get('fast'),
                                      file_control=file_control,
                                      archive_control=archive_control)
        sequence = '0, 1, 2, 3, 4, 5, 6'
        state_reporting = True
        report_files = self._e.report(valid_items,
                                      sequence=sequence,
                                      identifier='F',
                                      state_reporting=state_reporting,
                                      dry=True)

        # Check the contents of the report file.
        # Hardwiring states here which is crap.
        report_files.sort()

        # We should get NSW first.
        fh = open(report_files[0])
        received = fh.read()
        fh.close()
        expected = ('%s|%s|%s|%s|%s|%s|%s\n%s|%s|%s|%s|%s|%s|%s\n' %
                    ('REF1',
                     'JOB_KEY',
                     'PICKUP_TIME',
                     'PICKUP_POD',
                     'IDENTITY_TYPE',
                     'IDENTITY_DATA',
                     'ITEM_NBR',
                     'fast_connote_nbr_03',
                     '3',
                     self._now.isoformat(' ')[:-7],
                     'pod_name fast 03',
                     'Passport',
                     'fast identity 03',
                     'fast_item_nbr_03'))
        msg = 'Contents of Priority-based POD report file not as expected'
        self.assertEqual(received, expected, msg)

        # QLD,
        fh = open(report_files[1])
        received = fh.read()
        fh.close()
        expected = ('%s|%s|%s|%s|%s|%s|%s\n%s|%s|%s|%s|%s|%s|%s\n' %
                    ('REF1',
                     'JOB_KEY',
                     'PICKUP_TIME',
                     'PICKUP_POD',
                     'IDENTITY_TYPE',
                     'IDENTITY_DATA',
                     'ITEM_NBR',
                     'fast_connote_nbr_04',
                     '4',
                     convert_timezone(self._now.isoformat(' ')[:-7], 'QLD'),
                     'pod_name fast 04',
                     'License',
                     'fast identity 04',
                     'fast_item_nbr_04'))
        self.assertEqual(received, expected, msg)

        # SA,
        fh = open(report_files[2])
        received = fh.read()
        fh.close()
        expected = ('%s|%s|%s|%s|%s|%s|%s\n%s|%s|%s|%s|%s|%s|%s\n' %
                    ('REF1',
                     'JOB_KEY',
                     'PICKUP_TIME',
                     'PICKUP_POD',
                     'IDENTITY_TYPE',
                     'IDENTITY_DATA',
                     'ITEM_NBR',
                     'fast_connote_nbr_06',
                     '6',
                     convert_timezone(self._now.isoformat(' ')[:-7], 'SA'),
                     'pod_name fast 06',
                     'License',
                     'fast identity 06',
                     'fast_item_nbr_06'))
        self.assertEqual(received, expected, msg)

        # VIC.
        fh = open(report_files[3])
        received = fh.read()
        fh.close()
        expected = ('%s|%s|%s|%s|%s|%s|%s\n%s|%s|%s|%s|%s|%s|%s\n%s|%s|%s|%s|%s|%s|%s\n' %
                    ('REF1',
                     'JOB_KEY',
                     'PICKUP_TIME',
                     'PICKUP_POD',
                     'IDENTITY_TYPE',
                     'IDENTITY_DATA',
                     'ITEM_NBR',
                     'fast_connote_nbr_01',
                     '1',
                     convert_timezone(self._now.isoformat(' ')[:-7], 'VIC'),
                     'pod_name fast 01',
                     'License',
                     'fast identity 01',
                     'fast_item_nbr_01',
                     'fast_connote_nbr_05',
                     '5',
                     self._now.isoformat(' ')[:-7],
                     'pod_name fast 05',
                     'License',
                     'fast identity 05',
                     'fast_item_nbr_05'))
        self.assertEqual(received, expected, msg)

        # Check the POD files.
        pod_files = []
        bu_staging_dir = os.path.join(self._e._staging_dir, 'fast', 'out')
        for item in items:
            pod_file = os.path.join(bu_staging_dir, '%s.ps' % str(item[1]))
            pod_files.append(pod_file)

        received = get_directory_files_list(bu_staging_dir, '.*\.ps')
        expected = pod_files
        msg = 'POD file list not as expected'
        self.assertListEqual(sorted(received), sorted(expected), msg)

        # Clean up.
        self._e.reset()
        remove_files(report_files)
        remove_files(pod_files)
        os.rmdir(os.path.join(self._e.staging_dir, 'fast', 'out'))
        os.rmdir(os.path.join(self._e.staging_dir, 'fast'))
        self._e.set_staging_dir(value=None)
        self._e.set_signature_dir(value=None)
        self._e.db.rollback()

    @classmethod
    def tearDownClass(cls):
        cls._e = None
        os.removedirs(cls._dir)
        os.removedirs(cls._staging_dir)
        os.removedirs(cls._archive_dir)
        del cls._e
        del cls._dir
        del cls._staging_dir
        del cls._archive_dir
