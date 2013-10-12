__all__ = [
    "DaemonService",
]
import nparcel


class DaemonService(nparcel.utils.Daemon):
    """Common components for the Daemoniser facility.

    """
    _file = None
    _dry = False
    _batch = False

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False):
        super(DaemonService, self).__init__(pidfile=pidfile)

        self._file = file
        self._dry = dry
        self._batch = batch

    @property
    def file(self):
        return self._file

    def set_file(self, value):
        self._file = value

    @property
    def dry(self):
        return self._dry

    def set_dry(self, value=True):
        self._dry = value

    @property
    def batch(self):
        return self._batch

    def set_batch(self, value=True):
        self._batch = value
