__all__ = [
    "Xlwriter",
]
import nparcel

from nparcel.utils.log import log


class Xlwriter(nparcel.Writer):
    """Toll Parcel Portal Writer class.

    """
    def __init__(self, outfile=None):
        """Writer initialiser.

        """
        super(nparcel.Xlwriter, self).__init__(outfile=outfile)

    def __call__(self, data):
        """Class callable that writes list of tuple values in *data*.

        **Args:**
            *data*: list of tuples to write out

        """
        log.debug('Preparing "%s" for output' % self.outfile)
        fh = open(self.outfile, 'wb')

        fh.close()
