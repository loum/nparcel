import unittest2
import datetime
import tempfile
import os

import nparcel

# Current business_unit map:
BU = {'fast': 2}


class TestExporterFast(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._seq = '0, 1, 2, 3, 4, 5, 6'

        cls._e = nparcel.Exporter()

        # Prepare some sample data.
        # "agent" table.
        agents = [{'code': 'AG01',
                   'state': 'VIC'},
                  {'code': 'AG02',
                   'state': 'NSW'}]
        agent_vic = cls._e.db.insert(cls._e.db._agent.insert_sql(agents[0]))
        agent_nsw = cls._e.db.insert(cls._e.db._agent.insert_sql(agents[1]))

        cls._now = datetime.datetime.now()
        # "job" table.
        jobs = [{'card_ref_nbr': 'fast card ref 01',
                 'agent_id': agent_vic,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU.get('fast')},
                {'card_ref_nbr': 'fast card ref 02',
                 'agent_id': agent_nsw,
                 'job_ts': '%s' % cls._now,
                 'bu_id': BU.get('fast')}]
        sql = cls._e.db.job.insert_sql(jobs[0])
        cls._job_id_01 = cls._e.db.insert(sql=sql)
        sql = cls._e.db.job.insert_sql(jobs[1])
        cls._job_id_02 = cls._e.db.insert(sql=sql)

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
                     'identity_type_data': 'fast identity 02'}]

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
        sql = self._e.db.jobitem.collected_sql(business_unit=BU.get('fast'))
        self._e.db(sql)

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
                     'fast_item_nbr_01')])
        msg = 'Fast Exporter report line items not as expected'
        self.assertListEqual(received, expected, msg)

    def test_process_archive_ps_files(self):
        """End to end collected items -- archive ps files.
        """
        # Define the staging/signature directory.
        self._e.set_signature_dir(self._dir)
        self._e.set_staging_dir(self._staging_dir)

        # Prepare the signature files.
        bu = 'fast'
        sql = self._e.db.jobitem.collected_sql(business_unit=BU.get(bu))
        self._e.db(sql)
        items = []
        ps_files = []
        for row in self._e.db.rows():
            items.append(row)
            fh = open(os.path.join(self._e.signature_dir,
                                   '%s.ps' % str(row[1])), 'w')
            ps_files.append(fh.name)
            fh.close()
            fh = open(os.path.join(self._e.signature_dir,
                                   '%s.png' % str(row[1])), 'w')
            fh.close()

        # Check if we can source a staging directory.
        self._e.set_out_dir(business_unit=bu)
        file_control = {'ps': False,
                        'png': True}
        self._e.set_out_dir(business_unit='fast')
        valid_items = self._e.process(business_unit_id=BU.get('fast'),
                                      file_control=file_control)
        sequence = '0, 1, 2, 3, 4, 5, 6'
        report_file = self._e.report(valid_items, sequence=sequence)

        # Check the contents of the report file.
        fh = open(report_file)
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
                     'fast_connote_nbr_01',
                     '1',
                     self._now.isoformat(' ')[:-7],
                     'pod_name fast 01',
                     'License',
                     'fast identity 01',
                     'fast_item_nbr_01'))
        msg = 'Contents of Priority-based POD report file not as expected'
        self.assertEqual(received, expected, msg)

        # Check that the ps files are archived.
        archived_files = []
        for ps_file in ps_files:
            archived_files.append(os.path.join(self._archive_dir,
                                               os.path.basename(ps_file)))

        archive_dir_files = []
        for file in os.listdir(self._archive_dir):
            if file.endswith('.ps'):
                ps_file = os.path.join(self._archive_dir, file)
                archive_dir_files.append(ps_file)

        msg = 'Archived file list not as expected'
        self.assertListEqual(archived_files, archive_dir_files, msg)

        # Clean.
        self._e.reset()
        os.remove(report_file)

        for item in items:
            # Remove the signature files.
            sig_file = os.path.join(self._e._staging_dir,
                                    'fast',
                                    'out',
                                    '%s.png' % str(item[1]))
            os.remove(sig_file)

            for ps_file in ps_files:
                os.remove(os.path.join(self._archive_dir,
                                       os.path.basename(ps_file)))

            # Clear the extract_id timestamp.
            sql = """UPDATE job_item
SET extract_ts = null
WHERE id = %d""" % item[1]
            self._e.db(sql)

        os.rmdir(os.path.join(self._e.staging_dir, 'fast', 'out'))
        os.rmdir(os.path.join(self._e.staging_dir, 'fast'))
        self._e.set_staging_dir(value=None)
        self._e.set_signature_dir(value=None)

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
