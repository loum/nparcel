__all__ = [
    "Filter",
]
import nparcel
from nparcel.utils.log import log

# ParcelPoint records are only interested in the "Agent Id" field.
FIELDS = {'Agent Id': {'offset': 453,
                       'length': 4}}


class Filter(nparcel.Service):
    """Nparcel Filter object.

    """
    _parser = nparcel.Parser(fields=FIELDS)
    _filtering_rules = []

    def __init__(self, rules=None):
        super(nparcel.Filter, self).__init__()

        self.set_filtering_rules(rules)

    @property
    def parser(self):
        return self._parser

    @property
    def filtering_rules(self):
        return self._filtering_rules

    def set_filtering_rules(self, values):
        del self._filtering_rules[:]
        self._filtering_rules = []

        if values is not None:
            self._filtering_rules.extend(values)
            log.debug('Filter set filtering_rules to "%s"' %
                      str(self._filtering_rules))

    def process(self, raw_record):
        """Identifies ParcelPoint records.

        Valid Delivery Partner records are identified by an *Agent Id*
        that starts with a token in the :attr:`filtering_rules` list.

        **Args:**
            *raw_record*: raw record directly from a T1250 file

        *Returns:**
            boolean ``True`` if record is a ParcelPoint

            boolean ``False`` if record does not have an Agent Id

            ``None`` if an *other* scenario (typically not a ParcelPoint)

        """
        fields = self.parser.parse_line(raw_record)
        connote_literal = raw_record[0:20].rstrip()
        log.info('Conn Note: "%s" start parse ...' % connote_literal)

        agent_id = fields.get('Agent Id')
        msg = 'Conn Note/Agent Id "%s/%s"' % (connote_literal, agent_id)
        status = None
        if agent_id is None or not agent_id:
            status = False
            self.set_alerts('%s - missing Agent Id' % msg)

        log.debug('Filtering rules: %s' % str(self.filtering_rules))
        if status is None:
            for rule in self.filtering_rules:
                log.debug('Filtering value|token: "%s|%s"' %
                          (agent_id, rule))
                if agent_id.startswith(rule):
                    log.info('%s - matches criteria' % msg)
                    status = True
                    break

        log.info('Conn Note: "%s" parse complete' % connote_literal)

        return status
