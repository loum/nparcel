__all__ = [
    "HealthB2CConfig",
]
import ConfigParser

import top
from top.utils.log import log
from top.utils.setter import set_list


class HealthB2CConfig(top.B2CConfig):
    """:class:`top.HealthB2CConfig` captures the configuration items
    required for the ``tophealth`` facility.

    .. attribute:: health_processes

        the names of the processes to include in the health check

    """
    _health_processes = []

    @property
    def health_processes(self):
        return self._health_processes

    @set_list
    def set_health_processes(self, values=None):
        pass

    def __init__(self, file=None):
        """:class:`top.HealthB2CConfig` initialisation.
        """
        top.B2CConfig.__init__(self, file)

    def parse_config(self):
        """Read config items from the configuration file.

        """
        top.Config.parse_config(self)

        kwargs = [{'section': 'health',
                   'option': 'processes',
                   'var': 'health_processes',
                   'is_list': True,
                   'is_required': True}]
        for kw in kwargs:
            self.parse_scalar_config(**kw)

        try:
            health_procs = self.get('health', 'processes')
            self.set_health_processes(health_procs.split(','))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s health.processes list: %s' %
                      str(self.health_processes))
