__all__ = [
     "Mts",
]
import nparcel


class Mts(nparcel.Service):
    """Nparcel Mts class.
    """

    def __init__(self,
                 config='npmts.conf'):
        """Nparcel Mts initialisation.
        """
        self._config = nparcel.Config()
        self._config.set_config_file(config)

        db = None

        super(nparcel.Mts, self).__init__(db=db)
