__all__ = [
    "OnDeliveryB2CConfig",
]
import ConfigParser

import nparcel
from nparcel.utils.log import log
from nparcel.utils.setter import (set_scalar,
                                  set_list)


class OnDeliveryB2CConfig(nparcel.B2CConfig):
    """:class:`nparcel.OnDeliveryB2CConfig` captures the configuration items
    required for the ``topondeliveryd`` facility.

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

    .. attribute:: delivered_header

        string that represents the TransSend column header name for
        a delivered item (default ``latest_scan_event_action``)

    .. attribute:: delivered_event_key

        string that represents a delivered event (default ``delivered``)

    .. attribute:: scan_desc_header

         the scanned description column header in TransSend
         (default ``latest_scanner_description``)

    .. attribute:: scan_desc_keys

        list of :attr:`scan_desc_header` tokens to compare against
        (default ``IDS - TOLL FAST GRAYS ONLINE``)

    """
    _ondelivery_loop = 30
    _inbound_tcd = []
    _tcd_filename_format = None
    _uncollected_day_range = 14.0
    _file_cache_size = 5
    _delivered_header = 'latest_scan_event_action'
    _delivered_event_key = None
    _scan_desc_header = None
    _scan_desc_keys = []

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
    def sc4_delay_ids(self):
        return self.bu_ids_with_set_condition('delay_template_sc_4')

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

    @property
    def delivered_header(self):
        return self._delivered_header

    @set_scalar
    def set_delivered_header(self, value):
        pass

    @property
    def delivered_event_key(self):
        return self._delivered_event_key

    @set_scalar
    def set_delivered_event_key(self, value):
        pass

    @property
    def scan_desc_header(self):
        return self._scan_desc_header

    @set_scalar
    def set_scan_desc_header(self, value):
        pass

    @property
    def scan_desc_keys(self):
        return self._scan_desc_keys

    @set_list
    def set_scan_desc_keys(self, values=None):
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
        kwargs = [{'section': 'dirs',
                   'option': 'comms',
                   'var': 'comms_dir'},
                  {'section': 'transsend',
                   'option': 'delivered_header'},
                  {'section': 'transsend',
                   'option': 'delivered_header'},
                  {'section': 'transsend',
                   'option': 'delivered_event_key'},
                  {'section': 'transsend',
                   'option': 'scan_desc_header'},
                  {'section': 'transsend',
                   'option': 'scan_desc_keys',
                   'is_list': True}]
        for kw in kwargs:
            self.parse_scalar_config(**kw)

        kwargs = [{'section': 'comms_delivery_partners',
                   'is_list': True},
                  {'section': 'business_units',
                   'cast_type': 'int',
                   'is_required': True},
                  {'section': 'file_bu',
                   'cast_type': 'int',
                   'is_required': True}]
        for kw in kwargs:
            self.parse_dict_config(**kw)

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
        self.parse_scalar_config('primary_elect', 'tcd_filename_format')
        self.parse_scalar_config('primary_elect',
                                 'uncollected_day_range',
                                 cast_type='float')
        self.parse_scalar_config('primary_elect',
                                 'file_cache_size',
                                 cast_type='int')
