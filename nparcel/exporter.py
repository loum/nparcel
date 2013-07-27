__all__ = [
    "Exporter",
]
import nparcel
from nparcel.utils.log import log


class Exporter(object):
    """Nparcel Exporter.
    """

    def __init__(self, db=None):
        """Exporter oject initialiser.
        """
        log.debug('Creating an Exporter object')
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()
