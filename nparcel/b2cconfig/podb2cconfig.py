__all__ = [
    "PodB2CConfig",
]
import ConfigParser
import sys

import nparcel
from nparcel.utils.log import log


class PodB2CConfig(nparcel.B2CConfig):
    """:class:`nparcel.PodB2CConfig` captures the configuration items
    required for the ``nphealth`` facility.

    .. attribute:: pod_translator_loop

        time (seconds) between pod_translator_loop processing iterations

    .. attribute:: pod_dirs

        inbound directory location to look for exporter files to process

    .. attribute:: out_dir

        outbound directory to place transposed files

    .. attribute:: file_formats

        list of regular expressions that represent the type of files that
        can be parsed by the POD translator

    """
    _pod_translator_loop = 600
    _pod_dirs = []
    _out_dir = None
    _file_formats = []

    def __init__(self, file=None):
        """:class:`nparcel.PodB2CConfig` initialisation.
        """
        nparcel.B2CConfig.__init__(self, file)

    @property
    def pod_translator_loop(self):
        return self._pod_translator_loop

    def set_pod_translator_loop(self, value):
        self._pod_translator_loop = int(value)
        log.debug('%s pod_translator_loop set to %d' %
                  (self.facility, self.pod_translator_loop))

    @property
    def pod_dirs(self):
        return self._pod_dirs

    def set_pod_dirs(self, values=None):
        del self._pod_dirs[:]
        self._pod_dirs = []

        if values is not None:
            self._pod_dirs.extend(values)
        log.debug('%s pod_dirs set to: "%s"' %
                  (self.facility, self.pod_dirs))

    @property
    def out_dir(self):
        return self._out_dir

    def set_out_dir(self, value=None):
        self._out_dir = value
        log.debug('%s out_dir set to: "%s"' %
                  (self.facility, str(self.out_dir)))

    @property
    def file_formats(self):
        return self._file_formats

    def set_file_formats(self, values=None):
        del self._file_formats[:]
        self._file_formats = []

        if values is not None:
            self._file_formats.extend(values)
        log.debug('%s pod.file_formats set to "%s"' %
                  (self.facility, self.file_formats))

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        # These are the generic values that can be removed
        # after nparcel.B2CConfig is refactored.
        try:
            self.set_prod(self.get('environment', 'prod'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s environment.prod not in config: %s. Using "%s"' %
                      (self.facility, err, self.prod))

        try:
            self.set_support_emails(self.get('email', 'support').split(','))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s email.support: %s. Using %s' %
                      (self.facility, err, self.support_emails))

        try:
            self.set_archive_dir(self.get('dirs', 'archive'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('%s dirs.archive is a required item: %s' %
                         (self.facility, err))
            sys.exit(1)

        # POD specific.
        try:
            self.set_pod_translator_loop(self.get('timeout',
                                                  'pod_translator_loop'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s timeout.pod_translator_loop: %s. Using %d' %
                      (self.facility, err, self.pod_translator_loop))

        try:
            self.set_pod_dirs(self.get('dirs', 'pod_in').split(','))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s dirs.pod_in: %s. Using %s' %
                      (self.facility, err, self.pod_in))

        try:
            self.set_out_dir(self.get('pod', 'out_dir'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('%s pod.out_dir is a required config item: %s' %
                         (self.facility, err))
            sys.exit(1)

        try:
            tmp_vals = self.get('pod', 'file_formats')
            self.set_file_formats(tmp_vals.split(','))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s pod.file_formats: %s. Using "%s"' %
                      (self.facility, err, self.file_formats))
