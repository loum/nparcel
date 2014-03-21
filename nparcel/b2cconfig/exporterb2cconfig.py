all__ = [
    "ExporterB2CConfig",
]
import sys
import ConfigParser

import nparcel
from nparcel.utils.log import log


class ExporterB2CConfig(nparcel.B2CConfig):
    """:class:`nparcel.ExporterB2CConfig` captures the configuration items
    required for the ``npexporterd`` facility.

    .. attribute:: signature_dir

        directory where the Toll Parcel Portal places it's POD
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

    .. attribute:: item_nbr_header

        token used to identify the item number column in the Exporter report
        file

    .. attribute:: business_units (exporter)

        the list of business units to query for collected items

    """
    _signature_dir = None
    _exporter_dirs = []
    _connote_header = None
    _exporter_file_formats = []
    _item_nbr_header = None
    _business_units = {}

    def __init__(self, file=None):
        """ExporterB2CConfig initialisation.
        """
        nparcel.B2CConfig.__init__(self, file)

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
        nparcel.Config.parse_config(self)

        # These are the generic values that can be removed
        # after nparcel.B2CConfig is refactored.
        try:
            self.set_support_emails(self.get('email', 'support').split(','))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s email.support: %s. Using %s' %
                      (self.facility, err, self.support_emails))

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
        # after nparcel.B2CConfig is refactored.
        try:
            self.set_signature_dir(self.get('dirs', 'signature'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('%s dirs.signature is a required item: %s' %
                         (self.facility, err))
            sys.exit(1)

        try:
            self.set_file_bu(dict(self.items('file_bu')))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('%s file_bu section is a required item: %s' %
                         (self.facility, err))
            sys.exit(1)

        try:
            tmp_vals = self.get('dirs', 'exporter_in').split(',')
            self.set_exporter_dirs(tmp_vals)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s dirs.exporter_in: %s. Using "%s"' %
                      (self.facility, err, self.exporter_dirs))

        # These are the exporter specific config items.
        try:
            tmp_vals = self.get('exporter', 'file_formats')
            self.set_exporter_file_formats(tmp_vals.split(','))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s exporter.file_formats: %s. Using "%s"' %
                      (self.facility, err, self.exporter_file_formats))

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
