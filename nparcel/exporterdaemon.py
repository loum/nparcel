__all__ = [
    "ExporterDaemon",
]
import nparcel

class ExporterDaemon(nparcel.utils.Daemon):

    def __init__(self,
                 pidfile):
        super(ExporterDaemon, self).__init__(pidfile=pidfile)
