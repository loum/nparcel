__all__ = [
    "Parser",
]


class Parser(object):
    """1250 file parser.

    .. attribute:: fields

        A dictionary based data structure that identifies the elements
        of interest.

    """

    def __init__(self,
                 fields=None):
        """Parser initialisation.
        """
        if fields is not None:
            self._fields = fields
        else:
            self._fields = {}

    def parse_line(self, line):
        """
        **Args:**
            **line:** string of characters to extract fields from.

        **Returns:**

        """
        result = {}

        for field_name, field_settings in self.get_fields().iteritems():
            start = field_settings.get('offset')
            end = start + field_settings.get('length')
            value = line[start:end].rstrip()
            result[field_name] = value

        return result

    def get_fields(self):
        return self._fields

    def set_fields(self, value):
        if isinstance(value, dict):
            for k, v in value.iteritems():
                self._fields[k] = v
        else:
            raise TypeError('Token assignment expected dictionary')
