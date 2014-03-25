__all__ = [
    "HealthB2CConfig",
]
import ConfigParser

import nparcel
from nparcel.utils.log import log


class HealthB2CConfig(nparcel.B2CConfig):
    """:class:`nparcel.CommsB2CConfig` captures the configuration items
    required for the ``npcommsd`` facility.

    .. attribute:: health_processes

        the names of the processes to include in the health check

    """
    _health_processes = []

    @property
    def health_processes(self):
        return self._health_processes

    def set_health_processes(self, values=None):
        del self._health_processes[:]
        self._health_processes = []

        if values is not None:
            self._health_processes.extend(values)
        log.debug('%s health.processes set to: "%s"' %
                  (self.facility, self.health_processes))

    def __init__(self, file=None):
        """HealthB2CConfig initialisation.
        """
        nparcel.B2CConfig.__init__(self, file)

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        # These are the generic values that can be removed
        # after nparcel.B2CConfig is refactored.
        try:
            self.set_prod(self.get('environment', 'prod'))
        except AttributeError, err:
            log.debug('%s environment.prod not in config: %s. Using "%s"' %
                      (self.facility, err, self.prod))

        try:
            self.set_support_emails(self.get('email', 'support').split(','))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s email.support: %s. Using %s' %
                      (self.facility, err, self.support_emails))

        # Health specific.
        try:
            health_procs = self.get('health', 'processes')
            self.set_health_processes(health_procs.split(','))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s health.processes list: %s' %
                      str(self.health_processes))
