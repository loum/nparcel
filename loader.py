__all__ = [
    "Loader",
]
import nparcel
from nparcel.utils.log import log

FIELDS = {'Bar code': {'offset': 438,
                       'length': 15},
          'Agent Id': {'offset': 453,
                       'length': 4}}

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

        extra_items = [x for x in fields.keys() if x not in map.keys()]
        if extra_items:
            raise ValueError('Cannot map fields "%s"' %
                             ", ".join(extra_items))
        else:
            columns = dict((map.get(k), v) for (k, v) in fields.iteritems())

        return columns
