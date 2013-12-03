__all__ = [
    "Writer",
]
import nparcel


class Writer(object):
    """Toll Parcel Portal Writer class.
    """
    _outfile = None

    def __init__(self, outfile=None):
        """Writer initialiser.

        """
        if outfile is not None:
            self._outfile = outfile

    def outfile(self):
        return self._outfile

    @property
    def set_outfile(self, value=None):
        self._outfile = value
