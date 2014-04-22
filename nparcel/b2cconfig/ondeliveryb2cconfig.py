ll__ = [
    "OnDeliveryB2CConfig",
]
import ConfigParser

import nparcel
from nparcel.utils.log import log
from nparcel.utils.setter import (set_scalar,
                                  set_list)


class OnDeliveryB2CConfig(nparcel.B2CConfig):
    """:class:`nparcel.OnDeliveryB2CConfig` captures the configuration items
    required for the ``npondeliveryd`` facility.

    .. attribute:: ondelivery_loop

        time (seconds) between ondelivery processing iterations

    .. attribute:: inbound_tcd

        TCD Delivery Report inbound directory
        (default ``/var/ftp/pub/nparcel/tcd/in``)

    .. attribute:: tcd_filename_format

        regular expression format string for TCD delivery
        reports inbound filenames
        (default ``TCD_Deliveries_\d{14}\.DAT``)

    .. attribute:: uncollected_day_range

        limit uncollected parcel search to within nominated day range
        (default 14.0 days)

    .. attribute:: file_cache_size

        number of date-orderd TCD files to load during a processing loop
        (default 5)

    """
    _ondelivery_loop = 30
    _inbound_tcd = []
    _tcd_filename_format = None
    _uncollected_day_range = 14.0
    _file_cache_size = 5

    @property
    def ondelivery_loop(self):
        return self._ondelivery_loop

    @set_scalar
    def set_ondelivery_loop(self, value):
        pass

    @property
    def inbound_tcd(self):
        return self._inbound_tcd

    @set_list
    def set_inbound_tcd(self, values=None):
        pass

    @property
    def tcd_filename_format(self):
        return self._tcd_filename_format

    @set_scalar
    def set_tcd_filename_format(self, value):
        pass

    @property
    def pe_comms_ids(self):
        return self.bu_ids_with_set_condition('pe_comms')

    @property
    def sc4_comms_ids(self):
        return self.bu_ids_with_set_condition('on_del_sc_4')

    @property
    def uncollected_day_range(self):
        return self._uncollected_day_range

    @set_scalar
    def set_uncollected_day_range(self, value):
        pass

    @property
    def file_cache_size(self):
        return self._file_cache_size

    @set_scalar
    def set_file_cache_size(self, value):
        pass

    def __init__(self, file=None):
        """OnDeliveryB2CConfig initialisation.
        """
        nparcel.B2CConfig.__init__(self, file)

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        # Parse the generic items that are used across the daemon
        # suite first (these will be refactored later).
        self.parse_scalar_config('dirs', 'comms', var='comms_dir')
        self.set_business_units(dict(self.items('business_units')))
        self.set_file_bu(dict(self.items('file_bu')))

        # Business unit conditons.  No probs if they are missing -- will
        # just default to '0' (False) for each flag.
        try:
            self.set_cond(dict(self.items('conditions')))
        except ConfigParser.NoSectionError, err:
            log.debug('%s.conditions: "%s". Using "%s"' %
                      (self.facility, err, self.cond))

        # OnDelivery specific.
        self.parse_scalar_config('timeout',
                                 'ondelivery_loop',
                                 cast_type='int')
        self.parse_scalar_config('dirs',
                                 'tcd_in',
                                 var='inbound_tcd',
                                 is_list=True)
        self.parse_scalar_config('primary_elect',
                                 'tcd_filename_format')
        self.parse_scalar_config('primary_elect',
                                 'uncollected_day_range',
                                 cast_type='float')
        self.parse_scalar_config('primary_elect',
                                 'file_cache_size',
                                 cast_type='int')
