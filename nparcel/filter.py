__all__ = [
    "Filter",
]
import nparcel
from nparcel.utils.log import log

# ParcelPoint records are only interested in the "Agent Id" field.
FIELDS = {'Agent Id': {'offset': 453,
                       'length': 4}}


class Filter(nparcel.Service):
    """Filter class.

    """
    _parser = nparcel.Parser(fields=FIELDS)

    def __init__(self):
        nparcel.Service.__init__(self)

    @property
    def parser(self):
        return self._parser

    def process(self, raw_record, rules):
        """Identifies ParcelPoint records.

        Valid Delivery Partner records are identified by an *Agent Id*
        that starts with a token in the *rules* list.

        **Args:**
            *raw_record*: raw record directly from a T1250 file

        *Returns:**
            boolean ``True`` if record is a ParcelPoint

            boolean ``False`` if record does not have an Agent Id

            ``None`` if another scenario (typically does not match *rules*)

        """
        fields = self.parser.parse_line(raw_record)
        connote_literal = raw_record[0:20].rstrip()

        agent_id = fields.get('Agent Id')
        msg = 'Connote|Agent Id "%s|%s"' % (connote_literal, agent_id)
        status = None
        if agent_id is None or not agent_id:
            self.set_alerts('%s - missing Agent Id' % msg)
            status = False
        else:
            for rule in rules:
                log.debug('%s comparing rule "%s" ...' % (msg, rule))
                if agent_id.startswith(rule):
                    status = True
                    log.info('%s matched rule "%s"' % (msg, rule))
                    break

                log.debug('%s did not match rule "%s"' % (msg, rule))

        return status
