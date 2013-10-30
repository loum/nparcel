__all__ = [
    "Filter",
]
import nparcel
from nparcel.utils.log import log

# ParcelPoint records are only interested in the "Agent Id" field.
FIELDS = {'Agent Id': {'offset': 453,
                       'length': 4}}


class Filter(object):
    """Nparcel Filter object.

    """
    _parser = nparcel.Parser(fields=FIELDS)

    @property
    def parser(self):
        return self._parser

    def process(self, raw_record):
        """Identifies ParcelPoint records.

        Valid ParcelPoint records are identified by an *Agent Id*
        that starts with ``P``.

        **Args:**
            *raw_record*: raw record directly from a T1250 file

        *Returns:**
            boolean ``True`` if record is a ParcelPoint

            boolean ``False`` if record is not a ParcelPoint

            ``None`` if an *other* scenario (typically missing Agent Id)

        """
        status = None

        connote_literal = raw_record[0:20].rstrip()
        log.info('Conn Note: "%s" start parse ...' % connote_literal)
        fields = self.parser.parse_line(raw_record)
        agent_id = fields.get('Agent Id')
        msg = 'Conn Note/Agent Id "%s/%s"' % (connote_literal, agent_id)
        if agent_id is None or not agent_id:
            log.info('%s - missing Agent Id' % msg)
        elif agent_id.startswith('P'):
            log.info('%s - matches criteria' % msg)
            status = True
        else:
            log.info('%s - does not match criteria' % msg)
            status = False

        log.info('Conn Note: "%s" parse complete' % connote_literal)

        return status
