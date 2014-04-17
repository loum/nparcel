__all__ = [
    "CommsB2CConfig",
]
import sys
import ConfigParser

import nparcel
from nparcel.utils.log import log


class CommsB2CConfig(nparcel.B2CConfig):
    """:class:`nparcel.CommsB2CConfig` captures the configuration items
    required for the ``npcommsd`` facility.

    .. attribute:: *comms_loop*

        time (seconds) between comms notification iterations.

    .. attribute:: *comms_dir*

        directory where comms files are read from

    .. attribute:: comms_q_warning

        comms queue warning threshold.  If number of messages exceeds this
        threshold (and is under the :attr:`comms_q_error` threshold then a
        warning email notification is triggered

    .. attribute:: comms_q_error

        comms queue error threshold.  If number of messages exceeds this
        threshold then an error email notification is triggered and
        the comms daemon is terminated


    .. attribute:: *controlled_templates*

        list of comms templates that are controlled by the delivery
        period thresholds

    .. attribute:: *uncontrolled_templates*

        list of comms templates that are *NOT* controlled by the delivery
        period thresholds.  In other words, comms can be sent 24 x 7

    .. attribute:: *skip_days*

        list of days ['Saturday', 'Sunday'] to not send messages

    .. attribute:: send_time_ranges

        time ranges when comms can be sent

    """
    _comms_loop = 30
    _comms = None
    _comms_q_warning = 100
    _comms_q_error = 1000
    _controlled_templates = []
    _uncontrolled_templates = []
    _skip_days = ['Sunday']
    _send_time_ranges = ['08:00-19:00']

    def __init__(self, file=None):
        """CommsB2CConfig initialisation.
        """
        nparcel.B2CConfig.__init__(self, file)

    @property
    def comms_dir(self):
        return self._comms

    def set_comms_dir(self, value):
        self._comms = value
        log.debug('%s comms_dir set to "%s"' %
                  (self.facility, self.comms_dir))

    @property
    def comms_loop(self):
        return self._comms_loop

    def set_comms_loop(self, value):
        self._comms_loop = int(value)
        log.debug('%s comms_loop set to: %s (sec)' %
                  (self.facility, self.comms_loop))

    @property
    def comms_q_warning(self):
        return self._comms_q_warning

    def set_comms_q_warning(self, value):
        self._comms_q_warning = int(value)
        log.debug('%s comms_q_warning set to: %d' %
                  (self.facility, self.comms_q_warning))

    @property
    def comms_q_error(self):
        return self._comms_q_error

    def set_comms_q_error(self, value):
        self._comms_q_error = int(value)
        log.debug('%s comms_q_error set to: %d' %
                  (self.facility, self.comms_q_error))

    @property
    def controlled_templates(self):
        return self._controlled_templates

    def set_controlled_templates(self, values=None):
        del self._controlled_templates[:]
        self._controlled_templates = []

        if values is not None:
            self._controlled_templates.extend(values)
        log.debug('%s controlled_templates set to: "%s"' %
                  (self.facility, self.controlled_templates))

    @property
    def uncontrolled_templates(self):
        return self._uncontrolled_templates

    def set_uncontrolled_templates(self, values=None):
        del self._uncontrolled_templates[:]
        self._uncontrolled_templates = []

        if values is not None:
            self._uncontrolled_templates.extend(values)
        log.debug('%s uncontrolled_templates set to: "%s"' %
                  (self.facility, self.uncontrolled_templates))

    @property
    def skip_days(self):
        return self._skip_days

    def set_skip_days(self, values):
        del self._skip_days[:]
        self._skip_days = []

        if values is not None:
            self._skip_days.extend(values)
        log.debug('%s skip_days set to: "%s"' %
                  (self.facility, self.skip_days))

    @property
    def send_time_ranges(self):
        return self._send_time_ranges

    def set_send_time_ranges(self, values):
        del self._send_time_ranges[:]
        self._send_time_ranges = []

        if values is not None:
            self._send_time_ranges.extend(values)
        log.debug('%s send_time_ranges set to: "%s"' %
                  (self.facility, self.send_time_ranges))

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        # These are the generic values that can be removed
        # after nparcel.B2CConfig is refactored.
        self.parse_scalar_config('environment', 'prod')

        try:
            self.set_support_emails(self.get('email', 'support').split(','))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s email.support: %s. Using %s' %
                      (self.facility, err, self.support_emails))

        # These are the comms values that will remain
        # after nparcel.B2CConfig is refactored.
        try:
            self.set_comms_dir(self.get('dirs', 'comms'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('%s dirs.comms is a required config item: %s' %
                         (self.facility, err))
            sys.exit(1)

        try:
            self.set_comms_loop(self.get('timeout', 'comms_loop'))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s timeout.comms_loop: %s.  Using %d (sec)' %
                      (self.facility, err, self.comms_loop))

        try:
            tmp = self.get('comms', 'comms_queue_warning')
            self.set_comms_q_warning(tmp)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s comms.comms_queue_warning: %s.  Using "%d"' %
                      (self.facility, err, self.comms_q_warning))

        try:
            tmp = self.get('comms', 'comms_queue_error')
            self.set_comms_q_error(tmp)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s comms.comms_queue_error: %s.  Using "%d"' %
                      (self.facility, err, self.comms_q_error))

        try:
            tmp = self.get('comms', 'controlled_templates').split(',')
            self.set_controlled_templates(tmp)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s comms.controlled_templates: %s' %
                     (self.facility, err))

        try:
            tmp = self.get('comms', 'uncontrolled_templates').split(',')
            self.set_uncontrolled_templates(tmp)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('%s comms.uncontrolled_templates: %s' %
                      (self.facility, err))

        try:
            tmp = self.get('comms', 'skip_days').split(',')
            self.set_skip_days(tmp)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s comms.skip_days: %s.  Using "%s"' %
                      (self.facility, err, self.skip_days))

        try:
            tmp = self.get('comms', 'send_time_ranges').split(',')
            self.set_send_time_ranges(tmp)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('%s comms.send_time_ranges: %s.  Using "%s"' %
                      (self.facility, err, self.send_time_ranges))
