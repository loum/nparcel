all__ = [
    "ExporterB2CConfig",
]
import ConfigParser

import top
from top.utils.log import log
from top.utils.setter import (set_scalar,
                              set_list,
                              set_dict)


class ExporterB2CConfig(top.B2CConfig):
    """:class:`top.ExporterB2CConfig` captures the configuration items
    required for the ``topexporterd`` facility.

    .. attribute:: exporter_loop

        time (seconds) between exporter processing iterations

    .. attribute:: signature_dir

        directory where the Toll Outlet Portal places it's POD
        signature files

    .. attribute:: exporter_dirs

        directory list for file-based events to trigger a ``job_item``
        closure

    .. attribute:: connote_header

        token used to identify the connote column in the Exporter report
        file

    .. attribute:: exporter_file_formats

        list of regular expressions that represent the type of files that
        can be parsed by the exporter

    .. attribute:: exporter_fields

        dictionary of business unit exporter ordered columns

    .. attribute:: item_nbr_header

        token used to identify the item number column in the Exporter report
        file

    .. attribute:: business_units (exporter)

        the list of business units to query for collected items

    """
    _exporter_loop = 3600
    _signature_dir = None
    _exporter_dirs = []
    _connote_header = None
    _exporter_file_formats = []
    _exporter_fields = {}
    _item_nbr_header = None
    _business_units = {}

    @property
    def exporter_loop(self):
        return self._exporter_loop

    @set_scalar
    def set_exporter_loop(self, value):
        pass

    @property
    def signature_dir(self):
        return self._signature_dir

    @set_scalar
    def set_signature_dir(self, value):
        pass

    @property
    def exporter_dirs(self):
        return self._exporter_dirs

    @set_list
    def set_exporter_dirs(self, values=None):
        pass

    @property
    def exporter_file_formats(self):
        return self._exporter_file_formats

    @set_list
    def set_exporter_file_formats(self, values=None):
        pass

    @property
    def exporter_fields(self):
        return self._exporter_fields

    @set_dict
    def set_exporter_fields(self, values=None):
        pass

    @property
    def connote_header(self):
        return self._connote_header

    @set_scalar
    def set_connote_header(self, value):
        pass

    @property
    def item_nbr_header(self):
        return self._item_nbr_header

    @set_scalar
    def set_item_nbr_header(self, value=None):
        pass

    @property
    def business_units(self):
        return self._business_units

    def set_business_units(self, values=None):
        self._business_units.clear()

        if values is not None:
            self._business_units = values
            for k, v in self._business_units.iteritems():
                self._business_units[k] = int(v)
        log.debug('%s exporter.business_units set to: "%s"' %
                  (self.facility, self.business_units))

    def __init__(self, file=None):
        """ExporterB2CConfig initialisation.
        """
        top.B2CConfig.__init__(self, file)

    def parse_config(self):
        """Read config items from the configuration file.

        """
        top.Config.parse_config(self)

        kwargs = [{'section': 'timeout',
                   'option': 'exporter_loop',
                   'cast_type': 'int'},
                  {'section': 'dirs',
                   'option': 'signature',
                   'var': 'signature_dir',
                   'is_required': True},
                  {'section': 'dirs',
                   'option': 'staging_base',
                   'is_required': True},
                  {'section': 'dirs',
                   'option': 'archive',
                   'var': 'archive_dir',
                   'is_required': True},
                  {'section': 'dirs',
                   'option': 'exporter_in',
                   'var': 'exporter_dirs',
                   'is_list': True},
                  {'section': 'exporter',
                   'option': 'file_formats',
                   'var': 'exporter_file_formats',
                   'is_list': True},
                  {'section': 'exporter',
                   'option': 'connote_header'},
                  {'section': 'exporter',
                   'option': 'item_nbr_header'}]
        for kw in kwargs:
            self.parse_scalar_config(**kw)

        kwargs = [{'section': 'file_bu',
                   'cast_type': 'int',
                   'is_required': True},
                  {'section': 'conditions',
                   'var': 'cond'},
                  {'section': 'exporter_fields'},
                  {'section': 'business_units',
                   'cast_type': 'int',
                   'is_required': True}]
        for kw in kwargs:
            self.parse_dict_config(**kw)
