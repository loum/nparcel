__all__ = [
    "FilterDaemon",
]
import nparcel


class FilterDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.Filter` class.

    """
    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config='nparcel.conf'):
        super(FilterDaemon, self).__init__(pidfile=pidfile,
                                           file=file,
                                           dry=dry,
                                           batch=batch)

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()
