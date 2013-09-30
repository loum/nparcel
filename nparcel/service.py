__all__ = [
    "Service",
]
import nparcel
from nparcel.utils.files import create_dir


class Service(object):
    """Nparcel base-Service class.

    .. attribute:: db

        :class:`nparcel.DbSession` object

    .. attribute:: comms_dir

        directory where comms files are sent for further processing

    """
    _comms_dir = None

    def __init__(self, db=None, comms_dir=None):
        """Nparcel Service initialisation.

        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

    @property
    def comms_dir(self):
        return self._comms_dir

    def set_comms_dir(self, value):
        if create_dir(value):
            self._comms_dir = value
