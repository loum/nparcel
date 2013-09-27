__all__ = [
    "StopParser",
]


class StopParser(object):
    """GraysOnline Shipment Stop Report parser.

    .. attribute:: fields

        A dictionary based data structure that identifies the elements
        of interest.

    """
    _fields = {}

    def __init__(self, fields=None):
        """StopParser initialisation.
        """
        if fields is not None:
            self._fields = fields

    @property
    def fields(self):
        return self._fields

    def set_fields(self, value):
        if isinstance(value, dict):
            for k, v in value.iteritems():
                self._fields[k] = v
        else:
            raise TypeError('Token assignment expected dictionary')
