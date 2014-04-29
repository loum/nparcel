all__ = [
    "ExporterB2CConfig",
]
import sys
import ConfigParser

import top
from top.utils.log import log


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

    def set_exporter_loop(self, value):
        self._exporter_loop = int(value)
        log.debug('%s exporter_loop set to %d' %
                  (self.facility, self.exporter_loop))

    def __init__(self, file=None):
        """ExporterB2CConfig initialisation.
        """
        top.B2CConfig.__init__(self, file)

    @property
    def signature_dir(self):
        return self._signature

    def set_signature_dir(self, value):
        self._signature = value
        log.debug('%s signature_dir set to "%s"' %
                   (self.facility, self.signature_dir))

    @property
    def exporter_dirs(self):
        return self._exporter_dirs

    def set_exporter_dirs(self, values):
        del self._exporter_dirs[:]
        self._exporter_dirs = []

        if values is not None:
            self._exporter_dirs.extend(values)
        log.debug('%s exporter_dirs set to "%s"' %
                  (self.facility, self.exporter_dirs))

    @property
    def exporter_file_formats(self):
        return self._exporter_file_formats

    def set_exporter_file_formats(self, values=None):
        del self._exporter_file_formats[:]
        self._exporter_file_formats = []

        if values is not None:
            self._exporter_file_formats.extend(values)
        log.debug('%s exporter.file_formats set to "%s"' %
                  (self.facility, self.exporter_file_formats))

    @property
    def exporter_fields(self):
        return self._exporter_fields

    def set_exporter_fields(self, values=None):
        self._exporter_fields.clear()

        if values is not None:
            self._exporter_fields = values
        log.debug('%s exporter_fields set to: "%s"' %
                  (self.facility, self.exporter_fields))

    @property
    def connote_header(self):
        return self._connote_header

    def set_connote_header(self, value=None):
        self._connote_header = value
        log.debug('%s exporter.connote_header set to "%s"' %
                  (self.facility, self.connote_header))

    @property
    def item_nbr_header(self):
        return self._item_nbr_header

    def set_item_nbr_header(self, value=None):
        self.item_nbr_header = value
        log.debug('%s exporter.item_nbr_header set to: "%s"' %
                  (self.facility, self.item_nbr_header))

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

    def parse_config(self):
        """Read config items from the configuration file.

        """
        top.Config.parse_config(self)

        # These are the generic values that can be removed
        # after top.B2CConfig is refactored.
        try:
            self.set_staging_base(self.get('dirs', 'staging_base'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('%s dirs.staging_base is a required item: %s' %
                         (self.facility, err))
            sys.exit(1)

        try:
            self.set_archive_dir(self.get('dirs', 'archive'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('%s dirs.archive is a required item: %s' %
                         (self.facility, err))
            sys.exit(1)

        try:
            self.set_cond(dict(self.items('conditions')))
        except ConfigParser.NoSectionError, err:
            log.debug('%s conditions: %s. Using %s' %
                      (self.facility, err, self._cond))

        # These are the comms values that will remain
        # after top.B2CConfig is refactored.
        try:
            self.set_signature_dir(self.get('dirs', 'signature'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('%s dirs.signature is a required item: %s' %
                         (self.facility, err))
            sys.exit(1)

        kwargs = [{'section': 'file_bu',
                   'cast_type': 'int',
                   'is_required': True}]
        for kw in kwargs:
            self.parse_dict_config(**kw)

        try:
            tmp_vals = self.get('dirs', 'exporter_in').split(',')
            self.set_exporter_dirs(tmp_vals)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s dirs.exporter_in: %s. Using "%s"' %
                      (self.facility, err, self.exporter_dirs))

        # Exporter specific.
        try:
            self.set_exporter_loop(self.get('timeout', 'exporter_loop'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s timeout.exporter_loop: %s, Using %d' %
                      (self.facility, err, self.exporter_loop))

        try:
            tmp_vals = self.get('exporter', 'file_formats')
            self.set_exporter_file_formats(tmp_vals.split(','))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s exporter.file_formats: %s. Using "%s"' %
                      (self.facility, err, self.exporter_file_formats))

        try:
            self.set_exporter_fields(dict(self.items('exporter_fields')))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s exporter_fields: %s. Using "%s"' %
                      (self.facility, err, self.exporter_fields))

        try:
            self.set_connote_header(self.get('exporter', 'connote_header'))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s exporter.connote_header: %s. Using "%s"' %
                      (self.facility, err, self.connote_header))

        try:
            self.set_item_nbr_header(self.get('exporter',
                                              'item_nbr_header'))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s exporter.item_nbr_header: %s. Using "%s"' %
                      (self.facility, err, self.item_nbr_header))

        try:
            self.set_business_units(dict(self.items('business_units')))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s exporter.business_units: %s. Using "%s"' %
                      (self.facility, err, self.business_units))
