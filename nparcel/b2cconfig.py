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

    .. attribute loader_loop (loader)

        time (seconds) between loader processing iterations.

    .. attribute pe_loop (primary elect)

        time (seconds) between primary elect processing iterations.

    .. attribute:: exporter_loop (exporter)

        time (seconds) between exporter processing iterations.

    .. attribute:: business_units (exporter)

        the list of business units to query for collected items

    .. attribute:: cond (loader)

        dictionary of Business unit special condition flags

    .. attribute:: rest (loader)

        dictionary of RESTful interfaces for SMS and email

    .. attribute:: exporter_fields (exporter)

        dictionary of business unit exporter ordered columns

    """
    _proxy_scheme = 'https'

    def __init__(self, file=None):
        """Nparcel Config initialisation.
        """
        nparcel.Config.__init__(self, file)

        self.dirs_to_check = []
        self.archive = None
        self.signature = None
        self.loader_loop = 30
        self.pe_loop = 30
        self.exporter_loop = 900
        self.business_units = {}
        self.file_bu = {}
        self.support_emails = []
        self.cond = {}
        self.rest = {}
        self.exporter_fields = {}

    @property
    def in_dirs(self):
        return self.dirs_to_check

    @property
    def archive_dir(self):
        return self.archive

    @property
    def staging_base(self):
        return self.staging_base

    @property
    def signature_dir(self):
        return self.signature

    @property
    def loader_loop(self):
        return self.loader_loop

    @property
    def pe_loop(self):
        return self.pe_loop

    @property
    def exporter_loop(self):
        return self.exporter_loop

    @property
    def business_units(self):
        return self.business_units

    @property
    def file_bu(self):
        return self.file_bu

    @property
    def support_emails(self):
        return self.support_emails

    @property
    def cond(self):
        return self.cond

    @property
    def rest(self):
        return self.rest

    @property
    def exporter_fields(self):
        return self.exporter_fields

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

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        try:
            self.dirs_to_check = self.get('dirs', 'in').split(',')
            log.debug('Loader directories to check %s' %
                      str(self.dirs_to_check))

            self.archive = self.get('dirs', 'archive')
            log.debug('Loader archive directory %s' % self.archive)

            self.staging_base = self.get('dirs', 'staging_base')
            log.debug('Exporter staging base %s' % self.staging_base)

            self.signature = self.get('dirs', 'signature')
            log.debug('Exporter signature directory %s' % self.signature)

            self.business_units = dict(self.items('business_units'))
            log.debug('Exporter Business Units %s' %
                      self.business_units.keys())

            self.file_bu = dict(self.items('file_bu'))
            log.debug('Exporter File Business Units %s' % self.file_bu)
        except ConfigParser.NoOptionError, err:
            log.critical('Missing required config: %s' % err)
            sys.exit(1)

        # Optional items (defaults provided).
        try:
            self.loader_loop = int(self.get('timeout', 'loader_loop'))
        except ConfigParser.NoOptionError, err:
            log.warn('Loader loop time not provided: %s' % err)
            pass

        try:
            self.pe_loop = int(self.get('timeout', 'pe_loop'))
        except ConfigParser.NoOptionError, err:
            log.warn('Primary elect loop time not provided: %s' % err)
            pass

        try:
            self.exporter_loop = int(self.get('timeout', 'exporter_loop'))
        except ConfigParser.NoOptionError, err:
            log.warn('Exporter loop time not provided: %s' % err)
            pass

        try:
            self.support_emails = self.get('email',
                                                   'support').split(',')
        except ConfigParser.NoOptionError, err:
            log.warn('Support emails not provided: %s' % err)
            pass

        # Business unit conditons.  No probs if they are missing -- will
        # just default to '0' (False) for each flag.
        try:
            self.cond = dict(self.items('conditions'))
            log.debug('Business Unit conditions %s' % self.cond.keys())
        except ConfigParser.NoSectionError, err:
            log.warn('Missing Business Unit conditions in config')

        # RESTful APIs.  May not need these if facility is not required
        # by any of the BU's
        try:
            self.rest = dict(self.items('rest'))
            log.debug('RESTful APIs %s' % str(self.rest))
        except ConfigParser.NoSectionError, err:
            log.warn('No RESTful APIs in config')

        # Exporter business unit-based column output and ordering.
        # Default is to simply display order as per query.
        try:
            self.exporter_fields = dict(self.items('exporter_fields'))
            log.debug('Exporter fields %s' % str(self.exporter_fields))
        except ConfigParser.NoSectionError, err:
            log.warn('No Exporter column output ordering in config')

        # Reminder notification_delay.
        try:
            notification_delay = self.get('reminder', 'notification_delay')
            self.set_notification_delay(int(notification_delay))
            log.debug('Parsed reminder notification delay: "%s"' %
                      notification_delay)
        except ConfigParser.NoOptionError, err:
            log.warn('No configured reminder notification delay')
            self.set_notification_delay(None)

        # Reminder start_date.
        try:
            start_date = self.get('reminder', 'start_date')
            start_time = time.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.fromtimestamp(time.mktime(start_time))
            self.set_start_date(dt)
            log.debug('Parsed reminder start date: "%s"' % start_date)
        except ConfigParser.NoOptionError, err:
            log.warn('No configured reminder start date')
            self.set_start_date(None)

        # Reminder hold_period.
        try:
            hold_period = self.get('reminder', 'hold_period')
            self.set_hold_period(int(hold_period))
            log.debug('Parsed reminder hold period: "%s"' % hold_period)
        except ConfigParser.NoOptionError, err:
            log.warn('No configured reminder hold period')
            self.set_hold_period(None)

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
            log.error('Missing DB key via config: %s' % err)

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
            log.error('Config proxy: %s' % err)

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
            log.error('Config proxy: %s' % err)

        return kwargs
