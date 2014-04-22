__all__ = [
    "MapperB2CConfig",
]
import ConfigParser
import sys

import nparcel
from nparcel.utils.log import log


class MapperB2CConfig(nparcel.B2CConfig):
    """:class:`nparcel.MapperB2CConfig` captures the configuration items
    required for the ``npmapperd`` facility.

    .. attribute:: mapper_loop

        time (seconds) between mapper processing iterations.

    .. attribute:: pe_customer

        upstream provider of the T1250 files (default "gis")

    .. attribute:: mapper_in_dir

        inbound file directory.  This is where the mapper daemon checks
        for files to process

    .. attribute:: pe_in_file_format

        filename structure to parse for Primary Elect inbound
        (default 'T1250_TOL[PIF]_\d{14}\.dat')

    .. attribute:: pe_in_file_archive_string

        regular expression grouping structure for Primary Elect inbound
        filenames that represent the YYYYMMDD date sequence (default
        T1250_TOL[PIF]_(\d{8})\d{6}\.dat

    """
    _mapper_loop = 30
    _pe_customer = 'gis'
    _mapper_in_dirs = []
    _pe_in_file_format = 'T1250_TOL[PIF]_\d{14}\.dat'
    _pe_in_file_archive_string = 'T1250_TOL[PIF]_(\d{8})\d{6}\.dat'

    @property
    def mapper_loop(self):
        return self._mapper_loop

    def set_mapper_loop(self, value):
        self._mapper_loop = int(value)
        log.debug('%s mapper_loop set to %d' %
                  (self.facility, self.mapper_loop))

    @property
    def pe_customer(self):
        return self._pe_customer

    def set_pe_customer(self, value):
        self._pe_customer = value
        log.debug('%s pe_customer set to %d' %
                  (self.facility, self.pe_customer))

    @property
    def mapper_in_dirs(self):
        return self._mapper_in_dirs

    def set_mapper_in_dirs(self, values):
        del self._mapper_in_dirs[:]
        self._mapper_in_dirs = []

        if values is not None:
            self._mapper_in_dirs.extend(values)
        log.debug('%s mapper_in_dirs set to "%s"' %
                  (self.facility, self.mapper_in_dirs))

    @property
    def pe_in_file_format(self):
        return self._pe_in_file_format

    def set_pe_in_file_format(self, value):
        self._pe_in_file_format = value
        log.debug('%s pe_in_file_format set to "%s"' %
                  (self.facility, self.pe_in_file_format))

    @property
    def pe_in_file_archive_string(self):
        return self._pe_in_file_archive_string

    def set_pe_in_file_archive_string(self, value):
        self._pe_in_file_archive_string = value
        log.debug('%s pe_in_file_archive_string set to "%s"' %
                  (self.facility, self.pe_in_file_archive_string))

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        # These are the generic values that can be removed
        # after nparcel.B2CConfig is refactored.
        try:
            self.set_archive_dir(self.get('dirs', 'archive'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('%s dirs.archive is a required config item: %s' %
                         (self.facility, err))
            sys.exit(1)

        # Reminder specific.
        try:
            self.set_mapper_loop(self.get('timeout', 'mapper_loop'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s timeout.mapper_loop: %s. Using %d' %
                      (self.facility, err, self.mapper_loop))

        try:
            self.set_pe_customer(self.get('primary_elect', 'customer'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s primary_elect.customer: %s. Using "%s"' %
                      (self.facility, err, self.pe_customer))

        try:
            tmp = self.get('dirs', 'mapper_in')
            self.set_mapper_in_dirs(tmp.split(','))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('%s dirs.mapper_in is a required config item: %s' %
                         (self.facility, err))
            sys.exit(1)

        try:
            tmp = self.get('primary_elect', 'file_format')
            self.set_pe_in_file_format(tmp)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s primary_elect.file_format: %s. Using "%s"' %
                      (self.facility, err, self.pe_in_file_format))

        try:
            tmp = self.get('primary_elect', 'file_archive_string')
            self.set_pe_in_file_archive_string(tmp)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s primary_elect.file_archive_string: %s. Using %s' %
                      (self.facility, err, self.pe_in_file_archive_string))
