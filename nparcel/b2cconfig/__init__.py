__all__ = [
    "B2CConfig",
]
import sys
import __builtin__

import nparcel
import ConfigParser
from nparcel.utils.log import log
from nparcel.utils.setter import (set_scalar,
                                  set_list,
                                  set_dict)

FLAG_MAP = {'item_number_excp': 0,
            'send_email': 1,
            'send_sms': 2,
            'send_ps_file': 3,
            'send_png_file': 4,
            'state_reporting': 5,
            'pe_pods': 6,
            'aggregate_files': 7,
            'send_sc_1': 8,
            'send_sc_2': 9,
            'send_sc_4': 10,
            'delay_template_sc_4': 11,
            'ignore_sc_4': 12,
            'pe_comms': 13,
            'on_del_sc_4': 14,
            'archive_ps_file': 15,
            'archive_png_file': 16,
            'delay_template_sc_2': 17}


class B2CConfig(nparcel.Config):
    """B2CConfig class.

    :class:`nparcel.B2CConfig` captures the configuration items required
    by the Toll Parcel Portal B2C middleware.

    .. attribute:: prod

        hostname of the production instance

    .. attribute:: dirs_to_check (loader)

        list of directories to look for T1250 files

    .. attribute:: archive_dir

        base directory where working files are archived to

    .. attribute:: staging_base

        directory to place processed collected reports and signature files
        for further processing.

    .. attribute:: comms (loader, primary elect)

        directory where comms files are kept for further processing

    .. attribute:: aggregators (ParcelPoint processing)

        directory where T1250 loader files are aggregated for further
        processing

    .. attribute:: adp_dirs (ADP bulk load processing)

        directory list for ADP bulk load files (into ``agent`` table)

    .. attribute loader_loop (loader)

        time (seconds) between loader processing iterations.

    .. attribute onleilvery_loop (on delivery)

        time (seconds) between on delivery processing iterations.

    .. attribute:: filter_loop (filter)

        time (seconds) between filter processing iterations.

    .. attribute:: adp_loop (ADP bulk load)

        time (seconds) between filter processing iterations.

    .. attribute:: business_units

        dictionary of business units names and their bu_ids as per the
        business_units.id table column

    .. attribute:: t1250_file_format

        T1250 filename format

    .. attribute:: cond (loader)

        dictionary of Business unit special condition flags

    .. attribute:: email

        list of email addresses to be advised of support related processing
        issues

    .. attribute:: rest (loader)

        dictionary of RESTful interfaces for SMS and email

    .. attribute:: filter_customer

        downstream recipient of filtered T1250 files
        (default ``parcelpoint``)

    .. attribute:: filtering_rules

        list of tokens to match against the start of the agent code field

    .. attribute:: adp_headers

        dictionary of ``agent`` table columns to column headers in the
        ADP bulk insert file

    .. attribute:: adp_file_formats

        list of regular expressions that represent the type of files that
        can be parsed by the ADP loader

    .. attribute:: code_header

        special ADP bulk insert header name that relates to the
        ``agent.code`` column.  This value is used as a unique
        identifier during the agent insert process

    .. attribute:: delivery_partners

        list of "delivery_partner" table values

    .. attribute:: adp_default_passwords

        dictionary of delivery partner default passwords

    .. attribute:: comms_delivery_partners

        dictionary of Business Unit based list of Delivery Partners that
        will have comms event files created during the load process

    """
    _prod = None
    _dirs_to_check = []
    _archive = None
    _staging_base = None
    _comms_dir = None
    _aggregator_dirs = []
    _adp_dirs = []
    _loader_loop = 30
    _filter_loop = 30
    _adp_loop = 30
    _proxy_scheme = 'https'
    _business_units = {}
    _t1250_file_format = 'T1250_TOL.*\.txt'
    _file_bu = {}
    _cond = {}
    _support_emails = []
    _rest = {}
    _filter_customer = 'parcelpoint'
    _filtering_rules = ['P', 'R']
    _adp_headers = {}
    _adp_file_formats = []
    _code_header = None
    _delivery_partners = []
    _adp_default_passwords = {}
    _comms_delivery_partners = {}

    def __init__(self, file=None):
        """B2CConfig initialisation.
        """
        nparcel.Config.__init__(self, file)

    @property
    def prod(self):
        return self._prod

    def set_prod(self, value=None):
        self._prod = value
        log.debug('%s environment.prod set to "%s"' %
                  (self.facility, self.prod))

    @property
    def in_dirs(self):
        return self._dirs_to_check

    def set_in_dirs(self, values):
        del self._dirs_to_check[:]
        self._dirs_to_check = []

        if values is not None:
            self._dirs_to_check.extend(values)
        log.debug('%s in_dirs set to "%s"' % (self.facility, self.in_dirs))

    @property
    def archive_dir(self):
        return self._archive

    def set_archive_dir(self, value):
        self._archive = value
        log.debug('%s dirs.archive set to "%s"' %
                  (self.facility, self.archive_dir))

    @property
    def staging_base(self):
        return self._staging_base

    def set_staging_base(self, value):
        self._staging_base = value
        log.debug('%s dirs.staging_base set to "%s"' %
                  (self.facility, self.staging_base))

    @property
    def comms_dir(self):
        return self._comms_dir

    @set_scalar
    def set_comms_dir(self, value):
        pass

    @property
    def aggregator_dirs(self):
        return self._aggregator_dirs

    def set_aggregator_dirs(self, values):
        del self._aggregator_dirs[:]
        self._aggregator_dirs = []

        if values is not None:
            log.debug('Set config aggregator in directories "%s"' %
                      str(values))
            self._aggregator_dirs.extend(values)

    @property
    def adp_dirs(self):
        return self._adp_dirs

    def set_adp_dirs(self, values=None):
        del self._adp_dirs[:]
        self._adp_dirs = []

        if values is not None:
            self._adp_dirs.extend(values)
        log.debug('adp_dirs set to "%s"' % self.adp_dirs)

    @property
    def loader_loop(self):
        return self._loader_loop

    @set_scalar
    def set_loader_loop(self, value):
        pass

    @property
    def filter_loop(self):
        return self._filter_loop

    @property
    def adp_loop(self):
        return self._adp_loop

    @property
    def business_units(self):
        return self._business_units

    @set_dict
    def set_business_units(self, values=None):
        pass

    @property
    def t1250_file_format(self):
        return self._t1250_file_format

    @property
    def file_bu(self):
        return self._file_bu

    def set_file_bu(self, values=None):
        self._file_bu.clear()

        if values is not None:
            self._file_bu = values
            for k, v in self._file_bu.iteritems():
                self._file_bu[k] = int(v)
        log.debug('%s.file_bu "%s"' % (self.facility, self.file_bu))

    @property
    def support_emails(self):
        return self._support_emails

    @set_list
    def set_support_emails(self, values=None):
        pass

    @property
    def cond(self):
        return self._cond

    def set_cond(self, values=None):
        self._cond.clear()

        if values is not None:
            self._cond = values
        log.debug('%s.conditions "%s"' % (self.facility, self.cond))

    @property
    def rest(self):
        return self._rest

    @property
    def filter_customer(self):
        return self._filter_customer

    def set_filter_customer(self, value):
        self._filter_customer = value

    @property
    def filtering_rules(self):
        return self._filtering_rules

    def set_filtering_rules(self, values):
        del self._filtering_rules[:]
        self._filtering_rules = []

        if values is not None:
            self._filtering_rules.extend(values)
            log.debug('Config set filtering_rules to "%s"' %
                      str(self._filtering_rules))

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

    @property
    def adp_headers(self):
        return self._adp_headers

    def set_adp_headers(self, values=None):
        self._adp_headers.clear()

        if values is not None:
            self._adp_headers = values
            log.debug('Config ADP headers set to: "%s"' %
                      self.adp_headers)
        else:
            log.debug('Cleared ADP headers')

    @property
    def adp_file_formats(self):
        return self._adp_file_formats

    def set_adp_file_formats(self, values=None):
        del self._adp_file_formats[:]
        self._adp_file_formats = []

        if values is not None:
            self._adp_file_formats.extend(values)
            log.debug('Config ADP file format list: "%s"' %
                      self.adp_file_formats)

    @property
    def code_header(self):
        return self._code_header

    def set_code_header(self, value=None):
        if value is not None:
            self.code_header = value
            log.debug('Config set code_header to: "%s"' %
                      self.code_header)

    @property
    def delivery_partners(self):
        return self._delivery_partners

    def set_delivery_partners(self, values=None):
        del self._delivery_partners[:]
        self._delivery_partners = []

        if values is not None:
            self._delivery_partners.extend(values)
            log.debug('Config delivery partners list: "%s"' %
                      self.delivery_partners)

    @property
    def adp_default_passwords(self):
        return self._adp_default_passwords

    def set_adp_default_passwords(self, values=None):
        self._adp_default_passwords.clear()

        if values is not None:
            self._adp_default_passwords = values
            log.debug('Config ADP default passwords: "%s"' %
                      self.adp_default_passwords)

    @property
    def comms_delivery_partners(self):
        return self._comms_delivery_partners

    @set_dict
    def set_comms_delivery_partners(self, values=None):
        pass

    def db_kwargs(self):
        """Extract database connectivity information from the config.

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
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Missing DB key via config: %s' % err)

        return kwargs

    def ts_db_kwargs(self):
        """Extract TransSend database connectivity information from the
        config.

        Database connectivity information is taken from the
        ``[transsend_db]`` section in the configuration file.  A typical
        example is::

            [transsend_db]
            host = SIEDBDOD04
            user = nparcel
            password = <passwd>
            port = 1521
            sid = TRCOPUAT

        Base assumptions on "host" keyword.  No "host" means this must be a
        test scenario in which case the database session is a memory-based
        sqlite instance.

        **Returns:**
            dictionary-based data structure of the form::

                kwargs = {'host': ...,
                          'user': ...,
                          'password': ...,
                          'port': ...,
                          'sid': ...}

        """
        kwargs = None

        try:
            host = self.get('transsend_db', 'host')
            user = self.get('transsend_db', 'user')
            password = self.get('transsend_db', 'password')
            port = self.get('transsend_db', 'port')
            if port is not None and port:
                port = int(port)
            sid = self.get('transsend_db', 'sid')
            kwargs = {'host': host,
                      'user': user,
                      'password': password,
                      'port': port,
                      'sid': sid}
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.info('Missing TransSend DB key via config: %s' % err)

        return kwargs

    def proxy_kwargs(self):
        """Extract proxy connectivity information from the configuration.

        Proxy connectivity information is taken from the ``[proxy]``
        section in the configuration file.  A typical example is::

            [proxy]
            host = itproxy-farm.toll.com.au
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

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        try:
            self._dirs_to_check = self.get('dirs', 'in').split(',')
            log.debug('Loader directories to check %s' % str(self.in_dirs))

            self.set_archive_dir(self.get('dirs', 'archive'))
            self.set_staging_base(self.get('dirs', 'staging_base'))
            self.parse_scalar_config('dirs', 'comms', var='comms_dir')
            self.parse_dict_config('business_units', cast_type='int')
            self.set_file_bu(dict(self.items('file_bu')))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.critical('Missing required config: %s' % err)
            sys.exit(1)

        self.parse_scalar_config('environment', 'prod')

        try:
            self._t1250_file_format = self.get('files',
                                               't1250_file_format')
            log.debug('T1250 file format %s' % self.t1250_file_format)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default T1250 file format: %s' %
                      self.t1250_file_format)

        # Aggregator directories.
        try:
            agg_dirs = self.get('dirs', 'aggregator').split(',')
            self.set_aggregator_dirs(agg_dirs)
            log.debug('Aggregator directories %s' % self.aggregator_dirs)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Aggregator inbound directories: %s' %
                      self.aggregator_dirs)

        # ADP directories.
        try:
            tmp_vals = self.get('dirs', 'adp_in').split(',')
            self.set_adp_dirs(tmp_vals)
            log.debug('ADP in bound directories %s' % self.adp_dirs)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default ADP inbound directories: %s' %
                      self.adp_dirs)

        # Filter processing.
        try:
            self._filter_customer = self.get('filter', 'customer')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Filter customer: %s' %
                      self.filter_customer)
        try:
            tmp_vals = self.get('filter', 'fitering_rules')
            self._filtering_rules = tmp_vals.split(',')
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default Filtering rules: %s' %
                      self.filtering_rules)

        # Optional items (defaults provided).
        try:
            self.loader_loop = int(self.get('timeout', 'loader_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Loader loop: %d (sec)' %
                      self.loader_loop)

        try:
            self._filter_loop = int(self.get('timeout', 'filter_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default Filter loop: %d (sec)' %
                      self.filter_loop)

        try:
            self._adp_loop = int(self.get('timeout', 'adp_loop'))
        except ConfigParser.NoOptionError, err:
            log.debug('Using default ADP loop: %d (sec)' %
                      self.adp_loop)

        self.parse_scalar_config('email',
                                 'support',
                                 'support_emails',
                                 is_list=True)

        # Business unit conditons.  No probs if they are missing -- will
        # just default to '0' (False) for each flag.
        try:
            self.set_cond(dict(self.items('conditions')))
        except ConfigParser.NoSectionError, err:
            log.debug('%s.conditions: "%s". Using "%s"' %
                      (self.facility, err, self.cond))

        # RESTful APIs.  May not need these if facility is not required
        # by any of the BU's
        try:
            self._rest = dict(self.items('rest'))
            log.debug('RESTful APIs %s' % str(self._rest))
        except ConfigParser.NoSectionError, err:
            log.warn('No RESTful APIs in config')

        # ADP headers
        try:
            self.set_adp_headers(dict(self.items('adp_headers')))
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            log.debug('Using default ADP headers: %s' % self.adp_headers)

        # ADP file formats.
        try:
            tmp_vals = self.get('adp', 'file_formats')
            self.set_adp_file_formats(tmp_vals.split(','))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default ADP file formats: %s' %
                      str(self.adp_file_formats))

        # ADP file formats.
        try:
            self.set_code_header(self.get('adp', 'code_header'))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default DP code header: %s' %
                      str(self.code_header))

        # Delivery partners.
        try:
            tmp_vals = self.get('adp', 'delivery_partners')
            self.set_delivery_partners(tmp_vals.split(','))
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default DP code header: %s' %
                      str(self.delivery_partners))

        # Delivery partner default passwords.
        try:
            tmp_vals = dict(self.items('adp_default_passwords'))
            self.set_adp_default_passwords(tmp_vals)
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError), err:
            log.debug('Using default delivery partner passwords: %s' %
                      str(self.adp_default_passwords))

        # Comms Delivery Partners.
        self.parse_dict_config('comms_delivery_partners', is_list=True)

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

    def comms_map(self, bu):
        """The comms trigger has become somewhat of a convoluted mess
        with various use-cases.  This method returns the *bu* based comms
        flags in a simpler dictionary lookup.

        **Args:**
            *bu*: the name of the Business Unit.  Only the first 4
            characters are accepted.  For example, ``tolf_nsw`` will be
            interpreted as ``tolf``.

        **Returns:**
            dictionary structure of the comms flags similar to::
                {'send_email': False,
                 'send_sms': True}

        """
        log.debug('Generating comms_map for Business Unit "%s"' % bu)

        comms_map = {'send_email': False,
                     'send_sms': False}

        for k in comms_map.keys():
            comms_map[k] = self.condition(bu, k)

        return comms_map

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
                    log.debug('Facility "%s" required by "%s"' %
                              (flag, bu))
                    status = True
                    break
        else:
            log.debug('Conditions config item is not defined')

        return status

    def get_pod_control(self, bu, type='xfer'):
        """Return the *bu* control settings from the condition map
        values based on *type*.

        Supported values for *type* include:

        * **xfer** - POD files to be sent to the outbound staging area
          or delete

        * **archive** - send to the archive directory

        **Args:**
            *bu*: the name of the Business Unit.

        **Kwargs:**
            *type*: distinguish between POD file transfer (**xfer**)
            or archiving (**archive**) (default ``xfer`` or file transfer)

        **Returns:**
            dictionary representing all of the file control condition flags
            for the *bu*.  For example, if Business Unit has a
            ``send_ps_file`` flag ``0`` and ``send_png_file`` flag ``1``::

                {'ps': False,
                 'png': True}

        """
        pod_control = {}

        if type == 'xfer':
            pod_control['ps'] = self.condition(bu, 'send_ps_file')
            pod_control['png'] = self.condition(bu, 'send_png_file')
        elif type == 'archive':
            pod_control['ps'] = self.condition(bu, 'archive_ps_file')
            pod_control['png'] = self.condition(bu, 'archive_png_file')

        return pod_control

    def bu_to_file(self, bu_id):
        """Return the file_bu configuration option of a given *bu*.

        State-based BU to file translations are not supported.  For
        example, ``tolf_vic``.

        **Args:**
            *bu_id*: business unit id as defined under the business_units
            section of the config.  For example, 'priority' has a *bu_id*
            of 1

        **Returns:**
            ``file_bu`` string such as ``TOLP``, ``TOLF`` or ``TOLI``

        """
        file_code_for_bu = None

        if bu_id is not None:
            for file_bu in self.file_bu.keys():
                if len(file_bu) > 4:
                    # Not interested in the state based BU's.
                    continue
                if self.file_bu.get(file_bu) == bu_id:
                    file_code_for_bu = file_bu
                    break

        return file_code_for_bu

    def bu_ids_with_set_condition(self, flag):
        """Given condition *flag*, will traverse the condition map for
        all Business Units and return the Business Unit IDs for the set
        flags.

        **Args:**
            *flag*: string-based condition map flag to check.  For example,
            ``pe_comms``

        **Returns:**
            tuple structure with the Business Unit ID's whose *flag* is
            set

        """
        log.debug('Getting BU ids for set "%s" condition' % flag)

        set_bu_ids = []
        for bu_name, id in self.business_units.iteritems():
            if self.condition(self.bu_to_file(id), flag):
                set_bu_ids.append(int(id))

        set_bu_ids = tuple(sorted(set_bu_ids))
        log.debug('"%s" flag set BU ids: %s' % (flag, str(set_bu_ids)))

        return set_bu_ids

    def parse_scalar_config(self,
                            section,
                            option,
                            var=None,
                            cast_type=None,
                            is_list=False):
        """Helper method that can parse a scalar value based on
        *section* and *option* in the :mod:`ConfigParser` based
        configuration file and set *var* attribute with the value parsed.

        **Args:**
            *section*: the configuration file section.  For example
            ``[environment]``

            *option*: the configuration file section's options to
            parse.

        **Kwargs:**
            *var*: the target attribute name.  This can be omitted if
            the target attribute name is the same as *option*

            *cast_type*: cast the value parsed as *cast_type*.  If
            ``None`` is specified, then parse as a string

            *is_list*: boolean flag to indicate whether to parse the
            option values as a list (default ``False``)

        **Returns:**
            the value of the scalar option value parsed

        """
        value = None

        if var is None:
            var = option

        try:
            value = self.get(section, option)
            if cast_type is not None:
                caster = getattr(__builtin__, cast_type)
                value = caster(value)
            if is_list:
                value = value.split(',')
            setter = getattr(self, 'set_%s' % var)
            setter(value)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            try:
                getter = getattr(self, var)
                log.debug('%s %s.%s not defined.  Using "%s"' %
                          (self.facility, section, option, getter))
            except AttributeError, err:
                log.debug('%s %s.%s not defined: %s.' %
                          (self.facility, section, option, err))

        return value

    def parse_dict_config(self,
                          section,
                          var=None,
                          cast_type=None,
                          is_list=False):
        """Helper method that can parse a :mod:`ConfigParser` *section*
        and set the *var* attribute with the value parsed.

        :mod:`ConfigParser` sections will produce a dictionary structure.
        If *is_list* is ``True`` the section's options values will be
        treated as a list.  This will produce a dictionary of lists.

        **Args:**
            *section*: the configuration file section.  For example
            ``[comms_delivery_partners]``

        **Kwargs:**
            *var*: the target attribute name.  This can be omitted if
            the target attribute name is the same as *option*

            *cast_type*: cast the value parsed as *cast_type*.  If
            ``None`` is specified, then parse as a string

            *is_list*: boolean flag to indicate whether to parse the
            option values as a list (default ``False``)

        **Returns:**
            the value of the :mod:`ConfigParser` section as a dict
            structure

        """
        value = None

        if var is None:
            var = section

        try:
            tmp_value = dict(self.items(section))
            if is_list:
                for k, v in tmp_value.iteritems():
                    tmp_value[k] = v.split(',')

            if cast_type is not None:
                caster = getattr(__builtin__, cast_type)
                for k, v in tmp_value.iteritems():
                    if isinstance(v, (list)):
                        tmp_value[k] = [caster(x) for x in v]
                    else:
                        tmp_value[k] = caster(v)

            value = tmp_value
            setter = getattr(self, 'set_%s' % var)
            setter(value)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError), err:
            try:
                getter = getattr(self, var)
                log.debug('%s %s not defined.  Using "%s"' %
                          (self.facility, section, getter))
            except AttributeError, err:
                log.debug('%s %s not defined: %s.' %
                          (self.facility, section, err))

        return value
