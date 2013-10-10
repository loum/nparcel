__all__ = [
    "MapperDaemon",
]
import nparcel


class MapperDaemon(nparcel.utils.Daemon):
    """Daemoniser facility for the :class:`nparcel.Loader` class.

    """
    _file_to_process = None
    _dry = False
    _batch = False

    def __init__(self,
                 pidfile,
                 file_to_process=None,
                 dry=False,
                 batch=False,
                 config='nparcel.conf'):
        super(MapperDaemon, self).__init__(pidfile=pidfile)

        self._file = file
        self._dry = dry
        self._batch = batch

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()

    @property
    def file_to_process(self):
        return self._file_to_process

    def set_dry(self, value):
        self._dry = value

    @property
    def dry(self):
        return self._dry

    def set_dry(self, value):
        self._dry = value

    @property
    def batch(self):
        return self._batch

    def set_batch(self, value):
        self._batch = value
