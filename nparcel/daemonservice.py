__all__ = [
    "DaemonService",
]
import nparcel


class DaemonService(nparcel.utils.Daemon):
    """Common components for the Daemoniser facility.

    .. attributes:: file

        daemonisers can handle a single iteration if a file is provided

    .. attributes:: dry

        don't actually run, just report

    .. attributes:: batch

        single iteration

    .. attribute:: emailer

        :mod:`nparcel.Emailer` object

    .. attribute:: reporter

        :mod:`nparcel.Reporter` object

    .. aatribute:: loop

        integer value that represents the sleep period between
        processing iterations (default 30 seconds)

    """
    _file = None
    _dry = False
    _batch = False
    _emailer = nparcel.Emailer()
    _reporter = nparcel.Reporter()
    _loop = 30

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

    def set_file(self, value=None):
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

    @property
    def emailer(self):
        return self._emailer

    @property
    def reporter(self):
        return self._reporter

    @property
    def loop(self):
        return self._loop

    def set_loop(self, value):
        self._loop = value
