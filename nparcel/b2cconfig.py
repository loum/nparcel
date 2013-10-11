__all__ = [
    "B2CConfig",
]
import sys
import time
import datetime

import nparcel
import ConfigParser
from nparcel.utils.log import log

FLAG_MAP = {'item_number_excp': 0,
            'send_email': 1,
            'send_sms': 2,
            'send_ps_file': 3,
            'send_png_file': 4,
            'state_reporting': 5}


class B2CConfig(nparcel.Config):
    """Nparcel Config class.

    :class:`nparcel.Config` captures the configuration items required
    by the Nparcel B2C Replicator.

    .. attribute:: dirs_to_check (loader)

        list of directories to look for T1250 files.

    .. attribute:: archive (loader)

        directory to place processed T1250 files into.

    .. attribute:: staging_base (exporter)

        directory to place processed collected reports and signature files
        for further processing.

    .. attribute:: signature (exporter)

        directory where POD signature files are kept.

    .. attribute:: comms (loader, primary elect)

        directory where comms files are kept for further processing

    .. attribute loader_loop (loader)

        time (seconds) between loader processing iterations.

    .. attribute pe_loop (primary elect)

        time (seconds) between primary elect processing iterations.

    .. attribute reminder_loop (reminder)

        time (seconds) between primary elect processing iterations.

    .. attribute comms_loop (comms)

        time (seconds) between notification iterations.

    .. attribute:: exporter_loop (exporter)

        time (seconds) between exporter processing iterations.

    .. attribute:: business_units (exporter)

        the list of business units to query for collected items

    .. attribute:: cond (loader)

        dictionary of Business unit special condition flags

    .. attribute:: email

        list of email addresses to be advised of support related processing
        issues

    .. attribute:: rest (loader)

        dictionary of RESTful interfaces for SMS and email

    .. attribute:: notification_period (reminder)

        period (in seconds) that triggers a reminder notice

    .. attribute:: start_date (reminder)

        ignores records whose job_item.created_ts occurs before this date

    .. attribute:: hold_period (reminder)

        defines the time period (in seconds) since the job_item.created_ts
        that the agent will hold the parcel before being returned

    .. attribute:: skip_days (comms)

        list of days ['Saturday', 'Sunday'] to not send messages

    .. attribute:: send_time_ranges (comms)

        time ranges when comms can be sent

    .. attribute:: exporter_fields (exporter)

        dictionary of business unit exporter ordered columns

    """
    _dirs_to_check = []
    _pe_dirs_to_check = []
    _archive = None
    _staging_base = None
    _signature = None
    _comms = None
    _loader_loop = 30
    _pe_loop = 30
    _reminder_loop = 30
    _comms_loop = 30
    _exporter_loop = 900
    _proxy_scheme = 'https'
    _business_units = {}
    _file_bu = {}
    _cond = {}
    _support_emails = []
    _rest = {}
    _notification_delay = 345600
    _start_date = datetime.datetime(2013, 9, 10, 0, 0, 0)
    _hold_period = 691200
    _skip_days = ['Sunday']
    _send_time_ranges = ['08:00-19:00']
    _comms_q_warning = 100
    _comms_q_error = 1000
    _exporter_fields = {}
    _pe_in_file_format = """T1250_TOLI_\d{14}\.dat"""

    def __init__(self, file=None):
        """Nparcel Config initialisation.
        """
        nparcel.Config.__init__(self, file)

    @property
    def in_dirs(self):
        return self._dirs_to_check

    @property
    def pe_in_dirs(self):
        return self._pe_dirs_to_check

    @property
    def archive_dir(self):
        return self._archive

    @property
    def staging_base(self):
        return self._staging_base

    @property
    def signature_dir(self):
        return self._signature

    @property
    def comms_dir(self):
        return self._comms

    @property
    def loader_loop(self):
        return self.loader_loop

    @property
    def pe_loop(self):
        return self._pe_loop

    @property
    def reminder_loop(self):
        return self._reminder_loop

    @property
    def comms_loop(self):
        return self._comms_loop

    @property
    def exporter_loop(self):
        return self._exporter_loop

    @property
    def business_units(self):
        return self._business_units

    @property
    def file_bu(self):
        return self._file_bu

    @property
    def support_emails(self):
        return self._support_emails

    @property
    def cond(self):
        return self._cond

    @property
    def rest(self):
        return self._rest

    @property
    def exporter_fields(self):
        return self._exporter_fields

    @property
    def pe_in_file_format(self):
        return self._pe_in_file_format

    @property
    def notification_delay(self):
        return self._notification_delay

    def set_notification_delay(self, value):
        self._notification_delay = value

    @property
    def start_date(self):
        return self._start_date

    def set_start_date(self, value):
        self._start_date = value

    @property
    def hold_period(self):
        return self._hold_period

    def set_hold_period(self, value):
        self._hold_period = value

    @property
    def skip_days(self):
        return self._skip_days

    def set_skip_days(self, values):
        del self._skip_days[:]

        if values is not None:
            log.debug('Set skip days to "%s"' % str(values))
            self._skip_days.extend(values)
        else:
            self._skip_days = []

    @property
    def send_time_ranges(self):
        return self._send_time_ranges

    def set_send_time_ranges(self, values):
        del self._send_time_ranges[:]

        if values is not None:
            log.debug('Set send time ranges "%s"' % str(values))
            self._send_time_ranges.extend(values)
        else:
            self._send_time_ranges = []

    @property
    def comms_q_warning(self):
        return self._comms_q_warning

    def set_comms_q_warning(self, value):
        self._comms_q_warning = value

    @property
    def comms_q_error(self):
        return self._comms_q_error

    def set_comms_q_error(self, value):
        self._comms_q_error = value

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        try:
            self._dirs_to_check = self.get('dirs', 'in').split(',')
            log.debug('Loader directories to check %s' % str(self.in_dirs))

            self._archive = self.get('dirs', 'archive')
            log.debug('Loader archive directory %s' % self._archive)

            self._staging_base = self.get('dirs', 'staging_base')
            log.debug('Exporter staging base %s' % self._staging_base)

            self._signature = self.get('dirs', 'signature')
            log.debug('Exporter signature directory %s' % self._signature)

            self._comms = self.get('dirs', 'comms')
            log.debug('Comms file directory %s' % self._comms)

            self._business_units = dict(self.items('business_units'))
            log.debug('Exporter Business Units %s' %
                      self._business_units.keys())

            self._file_bu = dict(self.items('file_bu'))
            log.debug('Exporter File Business Units %s' % self._file_bu)
        except ConfigParser.NoOptionError, err:
            log.critical('Missing required config: %s' % err)
            sys.exit(1)

        # Primary elect work is only a temporary solution.
        try:
            self._pe_dirs_to_check = self.get('dirs', 'pe_in').split(',')
            log.debug('Primary Elect directories to check %s' %
                      str(self.pe_in_dirs))
        except ConfigParser.NoOptionError:
            log.warn('No Primary Elect inbound directories in config')

        # Optional items (defaults provided).
        try:
            self.loader_loop = int(self.get('timeout', 'loader_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Loader loop: %d (sec)' %
                      self.loader_loop)

        try:
            self._pe_loop = int(self.get('timeout', 'pe_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Primary Elect loop: %d (sec)' %
                      self.pe_loop)

        try:
            self._reminder_loop = int(self.get('timeout', 'reminder_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Reminder loop: %d (sec)' %
                      self.reminder_loop)

        try:
            self._comms_loop = int(self.get('timeout', 'comms_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Notifications loop: %d (sec)' %
                      self.comms_loop)

        try:
            self._exporter_loop = int(self.get('timeout', 'exporter_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Exporter loop: %d (sec)' %
                      self.exporter_loop)

        try:
            self._support_emails = self.get('email', 'support').split(',')
        except ConfigParser.NoOptionError, err:
            log.warn('Support emails not provided: %s' % err)

        # Business unit conditons.  No probs if they are missing -- will
        # just default to '0' (False) for each flag.
        try:
            self._cond = dict(self.items('conditions'))
            log.debug('Business Unit conditions %s' % self.cond.keys())
        except ConfigParser.NoSectionError, err:
            log.warn('Missing Business Unit conditions in config')

        # RESTful APIs.  May not need these if facility is not required
        # by any of the BU's
        try:
            self._rest = dict(self.items('rest'))
            log.debug('RESTful APIs %s' % str(self._rest))
        except ConfigParser.NoSectionError, err:
            log.warn('No RESTful APIs in config')

        # Exporter business unit-based column output and ordering.
        # Default is to simply display order as per query.
        try:
            self._exporter_fields = dict(self.items('exporter_fields'))
            log.debug('Exporter fields %s' % str(self._exporter_fields))
        except ConfigParser.NoSectionError, err:
            log.warn('No Exporter column output ordering in config')

        # Reminder notification_delay.
        try:
            notification_delay = self.get('reminder', 'notification_delay')
            self.set_notification_delay(int(notification_delay))
            log.debug('Parsed reminder notification delay: "%s"' %
                      notification_delay)
        except ConfigParser.NoOptionError, err:
            log.debug('Using default reminder notification delay: %d' %
                      self.notification_delay)

        # Reminder start_date.
        try:
            start_date = self.get('reminder', 'start_date')
            start_time = time.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.fromtimestamp(time.mktime(start_time))
            self.set_start_date(dt)
            log.debug('Parsed reminder start date: "%s"' % start_date)
        except ConfigParser.NoOptionError, err:
            log.debug('Using default reminder start date: %s' %
                      self.start_date)

        # Reminder hold_period.
        try:
            hold_period = self.get('reminder', 'hold_period')
            self.set_hold_period(int(hold_period))
            log.debug('Parsed reminder hold period: "%s"' % hold_period)
        except ConfigParser.NoOptionError, err:
            log.debug('Using default reminder hold period: %d' %
                      self.hold_period)

        # Comms skip_days.
        try:
            skip_days = self.get('comms', 'skip_days').split(',')
            self.set_skip_days(skip_days)
            log.debug('Parsed comms days to skip: "%s"' % skip_days)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), err:
            log.debug('Using default skip_days: %s' % str(self.skip_days))

        # Comms send_time_ranges.
        try:
            send_time_ranges = self.get('comms', 'send_time_ranges')
            self.set_send_time_ranges(send_time_ranges.split(','))
            log.debug('Parsed comms send time ranges: "%s"' %
                      send_time_ranges)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), err:
            log.debug('Using default send time ranges: %s' %
                      str(self.send_time_ranges))

        # Comms comms queue warning threshold.
        try:
            comms_q_warning = self.get('comms', 'comms_queue_warning')
            self.set_comms_q_warning(int(comms_q_warning))
            log.debug('Parsed comms queue warn threshold: "%s"' %
                      comms_q_warning)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), err:
            log.debug('Using default comms queue warning: %s' %
                      self.comms_q_warning)

        # Comms comms queue error threshold.
        try:
            comms_q_error = self.get('comms', 'comms_queue_error')
            self.set_comms_q_error(int(comms_q_error))
            log.debug('Parsed comms queue error threshold: "%s"' %
                      comms_q_error)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), err:
            log.debug('Using default comms queue error: %s' %
                      self.comms_q_error)

    def condition(self, bu, flag):
        """Return the *bu* condition *flag* value.

        **Args:**
            *bu*: the name of the Business Unit.

            *flag*: name of the flag to process.

        **Returns:**
            boolean ``True`` if flag is '1'

            boolean ``False`` if flag is '0' or undefined

        """
        status = False

        if self.cond:
            index = FLAG_MAP.get(flag)
            if index is None:
                log.debug('Condition map undefined flag "%s"' % flag)
            else:
                if self.cond.get(bu) is None:
                    log.debug('Condition map missing BU "%s" option' % bu)
                else:
                    # Finally, get the flag!!!
                    try:
                        status = self.cond.get(bu)[index]
                        log.debug('Condition map %s:%s is "%s"' %
                                  (bu, flag, status))
                    except IndexError, e:
                        status = 0
        else:
            log.debug('Conditions config item is not defined')

        return status == '1'

    def condition_map(self, bu):
        """Return the *bu* condition map values.

        **Args:**
            *bu*: the name of the Business Unit.  Only the first 4
            characters are accepted.  For example, ``tolf_nsw`` will be
            interpreted as ``tolf``.

        **Returns:**
            dict representing all of the condition flags for the *bu*

        """
        c_map = {}

        bu = bu[:4]
        for flag in FLAG_MAP.keys():
            status = self.condition(bu, flag)
            log.debug('bu/flag - status | %s/%s - %s' % (bu, flag, status))
            c_map[flag] = status

        return c_map

    def required_facility(self, flag):
        """Check the *flag* conditions as a set and return ``True`` if at
        least one of the flags is set.

        Verifies if the facility denoted by *flag* is a required component.

        **Args:**
            *flag*: the name of the flag as per the ``FLAG_MAP`` options to
            verify

        **Returns:**
            boolean ``True`` if any flag in the set is '1'

            boolean ``False`` if no flags in the set are '1'

        """
        log.debug('have facility check for flag %s' % flag)
        status = False

        if self.cond:
            for bu in self.cond.keys():
                if self.condition(bu, flag):
                    log.debug('Facility "%s" required by "%s"' % (flag, bu))
                    status = True
                    break
        else:
            log.debug('Conditions config item is not defined')

        return status

    def get_file_control(self, bu):
        """Return the *bu* file control settings from the condition map
        values.

        **Args:**
            *bu*: the name of the Business Unit.

        **Returns:**
            dictionary representing all of the file control condition flags
            for the *bu*.  For example, if Business Unit has a
            ``send_ps_file`` flag ``0`` and ``send_png_file`` flag ``1``::

                {'ps': False,
                 'png': True}

        """
        file_control = {}

        file_control['ps'] = self.condition(bu, 'send_ps_file')
        file_control['png'] = self.condition(bu, 'send_png_file')

        return file_control

    def bu_to_file(self, bu):
        """Return the file_bu configuration option of a given *bu*.

        State-based BU to file translations are not supported.  For example,
        tolf_vic

        **Args:**
            *bu*: business unit name as defined under the business_units
            section of the config.  For example, 'priority'.

        **Returns:**

        """
        file_code_for_bu = None

        bu_value = self.business_units.get(bu)

        if bu_value is not None:
            for file_bu in self.file_bu.keys():
                if len(file_bu) > 4:
                    # Not interested in the state based BU's.
                    continue
                if self.file_bu.get(file_bu) == bu_value:
                    file_code_for_bu = file_bu
                    break

        return file_code_for_bu

    def db_kwargs(self):
        """Extract database connectivity information from the configuration.

        Database connectivity information is taken from the ``[db]``
        section in the configuration file.  A typical example is::

            [db]
            driver = FreeTDS
            host = SQVDBAUT07
            database = Nparcel
            user = npscript
            password = <passwd>
            port =  1442

        Base assumptions on "host" keyword.  No "host" means this must be a
        test scenario in which case the database session is a memory-based
        sqlite instance.

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'driver': ...,
                          'host': ...,
                          'database': ...,
                          'user': ...,
                          'password': ...,
                          'port': ...}

        """
        kwargs = None

        try:
            host = self.get('db', 'host')
            driver = self.get('db', 'driver')
            database = self.get('db', 'database')
            user = self.get('db', 'user')
            password = self.get('db', 'password')
            port = self.get('db', 'port')
            if port is not None and port:
                port = int(port)
            kwargs = {'driver': driver,
                      'host': host,
                      'database': database,
                      'user': user,
                      'password': password,
                      'port': port}
        except ConfigParser.NoOptionError, err:
            log.info('Missing DB key via config: %s' % err)

        return kwargs

    def proxy_kwargs(self):
        """Extract proxy connectivity information from the configuration.

        Proxy connectivity information is taken from the ``[proxy]``
        section in the configuration file.  A typical example is::

            [proxy]
            host = auproxy-farm.toll.com.au
            user = <username>
            password = <passwd>
            port = 8080
            protocol = https

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'host': ...,
                          'user': ...,
                          'password': ...,
                          'port': ...,
                          'protocol': ...}

        """
        kwargs = None

        try:
            host = self.get('proxy', 'host')
            user = self.get('proxy', 'user')
            password = self.get('proxy', 'password')
            port = self.get('proxy', 'port')
            if port is not None and port:
                port = int(port)
            self._proxy_scheme = self.get('proxy', 'protocol')
            kwargs = {'host': host,
                      'user': user,
                      'password': password,
                      'port': port,
                      'protocol': self._proxy_scheme}
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.warn('Config proxy: %s' % err)

        return kwargs

    def proxy_string(self, kwargs=None):
        """Constructs a proxy string based on the *kwargs* dictionary
        structure or :attr:`proxy` attribute (in that order if *kwargs* is
        ``None``).

        **Kwargs:**
            *kwargs* as per the return value of the :meth:`proxy_kwargs`
            method

        **Returns:**
            string that could be fed directly into a HTTP/S header
            to handle proxy authentication in the request.  Example::

                http://loumar:<passwd>@auproxy-farm.toll.com.aus:8080

        """
        values = None
        if kwargs is not None:
            values = kwargs
        else:
            values = self.proxy_kwargs()
        proxy = None
        if values is not None:
            # Check if we have a username and password.
            if (values.get('user') is not None and
                values.get('password') is not None):
                proxy = ("%s:%s@" % (values.get('user'),
                                     values.get('password')))

            if values.get('host') is not None:
                proxy += values.get('host')

            if values.get('port') is not None:
                proxy += ':' + str(values.get('port'))

        return proxy

    @property
    def proxy_scheme(self):
        return self._proxy_scheme

    def set_proxy_scheme(self, value):
        self._proxy_scheme = value

    @property
    def sms_api_kwargs(self):
        """Extract SMS API information from the configuration.

        SMS API information is taken from the ``[rest]``
        section in the configuration file.  A typical example is::

            [rest]
            sms_api = https://api.esendex.com/v1.0/messagedispatcher
            sms_user = username
            sms_pw = password

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'api': ...,
                          'api_username': ...,
                          'api_password': ...}

        """
        kwargs = {'api': None,
                  'api_username': None,
                  'api_password': None}

        try:
            kwargs['api'] = self.get('rest', 'sms_api')
            kwargs['api_username'] = self.get('rest', 'sms_user')
            kwargs['api_password'] = self.get('rest', 'sms_pw')

        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.warn('Config proxy: %s' % err)

        return kwargs

    @property
    def email_api_kwargs(self):
        """Extract email API information from the configuration.

        Email API information is taken from the ``[rest]``
        section in the configuration file.  A typical example is::

            [rest]
            email_api = https://apps.cinder.co/tollgroup...
            email_user = username
            email_pw = password
            failed_email = loumar@tollgroup.com

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'api': ...,
                          'api_username': ...,
                          'api_password': ...,
                          'support': ...}

        """
        kwargs = {'api': None,
                  'api_username': None,
                  'api_password': None,
                  'support': None}

        try:
            kwargs['api'] = self.get('rest', 'email_api')
            kwargs['api_username'] = self.get('rest', 'email_user')
            kwargs['api_password'] = self.get('rest', 'email_pw')
            kwargs['support'] = self.get('rest', 'failed_email')

        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.warn('Config proxy: %s' % err)

        return kwargs
