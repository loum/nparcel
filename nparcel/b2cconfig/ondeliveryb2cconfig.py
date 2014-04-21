ll__ = [
    "OnDeliveryB2CConfig",
]
import nparcel
from nparcel.utils.setter import set_scalar


class OnDeliveryB2CConfig(nparcel.B2CConfig):
    """:class:`nparcel.OnDeliveryB2CConfig` captures the configuration items
    required for the ``npondeliveryd`` facility.

    .. attribute:: ondelivery_loop

        time (seconds) between ondelivery processing iterations

    """
    _ondelivery_loop = 30

    def __init__(self, file=None):
        """OnDeliveryB2CConfig initialisation.
        """
        nparcel.B2CConfig.__init__(self, file)

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        self.parse_scalar_config('timeout',
                                 'ondelivery_loop',
                                 cast_type='int')

    @property
    def ondelivery_loop(self):
        return self._ondelivery_loop

    @set_scalar
    def set_ondelivery_loop(self, value):
        pass
