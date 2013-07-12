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

        Barcode should exist.

        """
        status = True

        if not fields.get('Bar code'):
            raise ValueError('Missing barcode')
            status = False

        if status and not fields.get('Agent Id'):
            raise ValueError('Missing Agent Id')
            status = False

        return status
