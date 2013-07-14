__all__ = [
    "Loader",
]
import re

import nparcel
from nparcel.utils.log import log

FIELDS = {'Conn Note': {'offset': 0,
                        'length': 20},
          'Identifier': {'offset': 21,
                         'length': 20},
          'Consumer Name': {'offset': 41,
                            'length': 30},
          'Consumer Address 1': {'offset': 81,
                                 'length': 30},
          'Consumer Address 2': {'offset': 111,
                                 'length': 30},
          'Suburb': {'offset': 141,
                     'length': 30},
          'Post code': {'offset': 171,
                        'length': 4},
          'Bar code': {'offset': 438,
                       'length': 15},
          'Agent Id': {'offset': 453,
                       'length': 4},
          'Pieces': {'offset': 588,
                     'length': 5}}
JOB_MAP = {'Agent Id': {
               'column': 'agent_id',
               'required': True},
           'Bar code': {
               'column': 'card_ref_nbr',
               'required': True},
           'Identifier': {
               'column': 'bu_id',
               'required': True,
               'callback': 'translate_bu_id'},
           'Consumer Address 1': {
               'column': 'address_1'},
           'Consumer Address 2': {
               'column': 'address_2'},
           'Suburb': {
               'column': 'suburb'},
           'Post code': {
               'column': 'postcode'},
           'state': {
               'column': 'state'},
           'status': {
               'column': 'status',
               'required': True,
               'default': 1}}
BU_MAP = {'TOLP': 1,
          'TOLF': 2,
          'TOLI': 3}


class Loader(object):
    """Nparcel Loader object.
    """

    def __init__(self):
        """
        """
        self.parser = nparcel.Parser(fields=FIELDS)

    def process(self, raw_record):
        """
        Extracts, validates and inserts an Nparcel record.

        **Args:**
            raw_record: raw record directly from a T1250 file.
        """
        status = True

        try:
            fields = self.parser.parse_line(raw_record)
        except Exception, err:
            # TODO -- handle the error alerting
            status = False
            log.error(err)

        if status:
            try:
                self.validate(fields)
            except ValueError, err:
                # TODO -- handle the error alerting
                status = False
                log.error(err)

        return status

    def validate(self, fields):
        """Perform some T1250 validations around:

        Barcode and Agent ID should exist.

        """
        status = True

        if not fields.get('Bar code'):
            raise ValueError('Missing barcode')
            status = False

        if status and not fields.get('Agent Id'):
            raise ValueError('Missing Agent Id')
            status = False

        return status

    def table_column_map(self, fields, map):
        """Convert the parser fields to Nparcel table column names in
        preparation for table manipulation.

        Runs a preliminary check to ensure that all items in *fields*
        can be mapped.  Raises a ``ValueError`` if otherwise.

        **Args:**
            fields: dictionary of :class:`nparcel.Parser` fields and
            values.

            map: dictionary of :class:`nparcel.Parser` fields to table
            columns.

        **Returns:**
            dictionary of table columns and values in the form::

                {'<column_1>': '<value>',
                 '<column_2>': '<value>'
                 ...}

        **Raises:**
            ValueError if all *fields* cannot be mapped.

        """
        columns = {}

        for field_name, v in map.iteritems():
            # Check for callbacks.
            if v.get('callback'):
                callback = getattr(self, v.get('callback'))
                fields[field_name] = callback(fields[field_name])

            if (v.get('required') and
                not fields.get(field_name) and
                not v.get('default')):
                raise ValueError('Field "%s" is required' % field_name)

            if not fields.get(field_name):
                fields[field_name] = v.get('default')

        columns = dict((map.get(k).get('column'),
                        fields.get(k)) for (k, v) in map.iteritems())

        return columns

    def translate_bu_id(self, value):
        """
        """
        bu_id = None

        log.debug('Translating "%s" to BU ...' % value)
        m = re.search(' YMLML11(TOL.).*', value)
        bu_id = BU_MAP.get(m.group(1))

        if bu_id is None:
            log.error('Unable to extract BU from "%s"' % value)

        return bu_id
