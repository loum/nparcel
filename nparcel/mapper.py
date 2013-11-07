__all__ = [
    "Mapper",
]
import nparcel
from nparcel.utils.log import log

# Primary Elect does not support the concept of a Barcode.  To satisfy
# the system, we copy over the first 15 characters of the Conn Note.
FIELDS = {'Conn Note': {'offset': 0,
                        'length': 20},
          'Identifier': {'offset': 22,
                         'length': 17},
          'System Identifier': {'offset': 29,
                                'length': 4},
          'ADP Type': {'offset': 39,
                       'length': 2},
          'Consumer Name': {'offset': 201,
                            'length': 86},
          'Consumer Address 1': {'offset': 81,
                                 'length': 30},
          'Consumer Address 2': {'offset': 111,
                                 'length': 30},
          'Suburb': {'offset': 141,
                     'length': 30},
          'Post code': {'offset': 171,
                        'length': 6},
          'Bar code': {'offset': 0,
                       'length': 15},
          'Pieces': {'offset': 588,
                     'length': 5},
          'Agent Id or Location Id': {'offset': 663,
                                      'length': 4},
          'Item Number': {'offset': 887,
                          'length': 32},
          'Mobile Number': {'offset': 925,
                            'length': 10},
          'Email Address': {'offset': 997,
                            'length': 60}}

MAP = {'Conn Note': {'offset': 0},
       'Identifier': {'offset': 22},
       'Consumer Name': {'offset': 41},
       'Consumer Address 1': {'offset': 81},
       'Consumer Address 2': {'offset': 111},
       'Suburb': {'offset': 141},
       'Post code': {'offset': 171},
       'Bar code': {'offset': 438},
       'Pieces': {'offset': 588},
       'Agent Id or Location Id': {'offset': 453},
       'Email Address': {'offset': 765},
       'Mobile Number': {'offset': 825},
       'Service Code': {'offset': 842},
       'Item Number': {'offset': 887}}


class Mapper(object):
    """Nparcel Mapper object.

    """
    _parser = nparcel.Parser(fields=FIELDS)

    def __init__(self):
        """Nparcel Mapper initialiser.

        """
        pass

    def process(self, raw):
        """Accepts an unformatted T1250 record *raw* and processes the
        translation to Nparcel T1250 format.

        **Args:**
            *raw*: the source record to translate

        **Returns:**
            string representation of a Nparcel T1250 record (1248 character
            length)

        """
        translated_line = tuple()
        parsed_dict = self.parser.parse_line(raw)
        connote_nbr = parsed_dict.get('Conn Note')
        log.info('Processing connote: "%s" ...' % connote_nbr)

        if (parsed_dict.get('ADP Type') is not None and
            parsed_dict.get('ADP Type') == 'PE'):
            log.info('Connote "%s" has a PE flag' % connote_nbr)
            bu = parsed_dict.get('System Identifier')

            # Need to fudge the Identifier field constant, 'YMLML11'.
            identifier_str = parsed_dict.get('Identifier')
            if identifier_str is not None:
                parsed_dict['Identifier'] = ('%s%s' % ('YMLML11',
                                                       identifier_str[7:]))
            translated_line = (bu, self.translate(parsed_dict))

        return translated_line

    def translate(self, data):
        """Translate source record into Nparcel T1250 format.

        Special characteristic here is that it will fudge a *Service Code*
        of "3" to denote a Primary Elect job.

        **Args:**
            *data*: dictionary structure representation of the raw record

        **Returns:**
            string representation of a Nparcel T1250 record (1248 character
            length)

        """
        translated_list = [' '] * 1248

        for k, v in MAP.iteritems():
            log.info('Mapping field "%s" ...' % k)

            key_offset = v.get('offset')
            if key_offset is None:
                log.warn('Mapping offset for key %s not defined' % k)
                continue

            log.debug('Mapping offset for key %s: %s' % (k, key_offset))
            log.debug('Raw value is "%s"' % data.get(k))

            index = 0
            data['Service Code'] = '3'
            for i in list(data.get(k)):
                translated_list[key_offset + index] = i
                index += 1

        translated_line = ''.join(translated_list)

        return translated_line

    @property
    def parser(self):
        return self._parser
