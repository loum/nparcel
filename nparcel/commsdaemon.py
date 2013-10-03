__all__ = [
    "CommsDaemon",
]
import nparcel


class CommsDaemon(nparcel.utils.Daemon):
    """CommsDaemon class.

    """
    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 config='nparcel.conf'):
        super(CommsDaemon, self).__init__(pidfile=pidfile)

        self.file = file
        self.dry = dry

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()
