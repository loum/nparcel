.. Toll Parcel Portal B2C Environment Initialisation

.. toctree::
    :maxdepth: 2

.. _environment_initialisation:

Environment Initialisation
==========================

The middleware B2C software package is available to all system users.
However, the environment needs to be initialised and configured for any of
the functionality to be useful.

Fresh Install
-------------

The ``topinit`` command creates the required directory structure and places
the required templates and configuration files in the default location.

.. _topinit-usage:

``topinit`` Usage
++++++++++++++++++

::

    usage: topinit [options]
    
    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity
      -d, --dry             dry run - show what would have been done
      -c CONFIG, --config=CONFIG
                            override default config

``topinit`` with the dry flag is a useful starting point as it will only
display to the terminal the files and directories that will be required::

    $ topinit -d
    Logging verbosity set to "INFO" level
    Processing dry run True
    Starting topinit ...
    Preparing environment in "/home/guest/.top"
    Copying "/usr/lib/python2.4/site-packages/nparcel/conf/init.conf.0.34"
    ...

``topinit`` will create the base directory structure in the ``.top``
directory off the current user's home directory.

Keys Files at a Glance ...
++++++++++++++++++++++++++
As of *release 0.34*, the required directory structure is as follows::

    $ tree .top
    .top
    |-- conf
    |   |-- init.conf
    |   |-- init.conf.0.34
    |   |-- log.conf.0.34
    |   |-- top.conf.0.34
    |   `-- ftp.conf.0.34
    |-- logs
    `-- templates
        |-- email_body_html.t
        |-- email_delay_html.t
        |-- email_general_err_html.t
        |-- email_health_html.t
        |-- email_html.t
        |-- email_message_q_err_html.t
        |-- email_message_q_warn_html.t
        |-- email_non_prod_html.t
        |-- email_pe_html.t
        |-- email_proc_err_html.t
        |-- email_rem_html.t
        |-- email_report_html.t
        |-- email_ret_html.t
        |-- email_test_html.t
        |-- err_html.t
        |-- sms_body_xml.t
        |-- sms_delay_xml.t
        |-- sms_non_prod.t
        |-- sms_pe_xml.t
        |-- sms_rem_xml.t
        |-- sms_ret_xml.t
        |-- sms_test_xml.t
        |-- subject_body_html.t
        |-- subject_delay_html.t
        |-- subject_err.t
        |-- subject_general_err_html.t
        |-- subject_health_html.t
        |-- subject_pe_html.t
        |-- subject_proc_err_html.t
        |-- subject_rem_html.t
        |-- subject_report_html.t
        |-- subject_ret_html.t
        `-- subject_test_html.t

The main directories are:

* ``conf`` - middleware B2C configuration files
* ``templates`` - template file used by the middleware B2C comms facility

Enable the Logger Handlers
++++++++++++++++++++++++++
Log handlers manage the log files and need to be configured::

    $ cd ~/.top
    $ ln -s conf/log.conf.0.34 log.conf

Set the Default Configuration
+++++++++++++++++++++++++++++
All commands use some form of configuration.  By default, the middleware B2C
components look for the default config at ``~.top/top.conf``::

    $ toploaderd status
    2013-10-08 17:26:04,266 CRITICAL:: Unable to locate config file:
    "/home/guest/.top/top.conf"

.. note::
    The default config settings are explained in the :ref:`config_items`

As a start, we can use the package-provided default::

    $ cd ~/.top
    $ ln -s conf/top.conf.0.34 top.conf

From here we should get some sane information::

    $ toploaderd status
    toploaderd is idle

Provide Database Connection Details
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For the middleware B2C tools to be useful, you will need to add the database
instance connection details into the ``top.conf`` configuration file.
By default, a new ``top.conf`` configuration file features a section
stub::

    [db]

Enter your database instance credential details under the ``[db]`` section
stub similar to the following::

    [db]
    driver = FreeTDS
    host = sqvdbaut07
    database = Nparcel
    user = npscript
    password = <password>
    port =  1442

Verify the Conditions Mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The default configuration mappings are provided as a generalisation of the
Business Unit requirements during development.  These may have been modified
during production and should be verified.

The default settings for the condition map in *release 0.34* are as
follows::

    [conditions]
    #      000000000111111111
    #      123456789012345678
    TOLP = 000100000000010110
    TOLF = 000101100000010110
    TOLI = 100010000000010110

Adjust these to align with your environments requirements.

Supply the Esendex REST Credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If the middleware B2C comms facility is to be used, then supply the Esendex
API credentials for both email and SMS under the ``[rest]`` configuration
section::

    [rest]
    sms_api = https://api.esendex.com/v1.0/messagedispatcher
    sms_user = <username>
    sms_pw = <password>

    email_api = https://apps.cinder.co/tollgroup/wsemail/emailservice.svc/sendemail
    email_user = <username>
    email_pw = <password>

Verify the Supplied Defaults
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Where possible, the new package ``top.conf`` file tries to provide sane
defaults for the various facilities.  Adjust these to suit your
requirements.

Set the Outbound FTP Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The outbound FTP service has its own configuration file, ``ftp.conf``.
``topinit`` will provide a package version-based default but this needs to
be linked to the appropriate location::

    $ cd ~/.top
    $ ln -s conf/ftp.conf.0.34 ftp.conf

Upgrade
-------
:ref:`topinit <topinit-usage>` can again be used to prepare the environment during a package
upgrade.  ``topinit`` will ensure that the required files (new or existing)
are put in their correct place.

Certain configuration files (such as ``top.conf`` and ``ftp.conf``)
are not clobberred as to not override interface connection credentials.  In
this case, an additional manual step would be required to copy over the
connection credentials into the new, package-versioned configuration file and
relink.

``topinit`` arranges files into two categories:

* **unconditional** - existing files are clobberred to conform to the
  requirments of the package software

* **conditional** - copy file over only if it does not already exist

.. note::
    a backup of the existing file is made if the file to copy is flagged
    as **unconditional**

Verify Existing Options
+++++++++++++++++++++++
If your existing configuration arrangement features customisations, ensure
that you copy these over to the new ``top.conf`` file.

The defaults are a good starting point but probably not what you require.

Starting the Daemons
--------------------

As of *version 0.32*, ``topctrl`` can be used to start and stop all
middleware daemons in a single call.

``topctrl`` Usage
+++++++++++++++++

::

    topctrl -h
    usage: topctrl [options] start|stop|status

    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity

For example::

    $ topctrl start
    Starting toploaderd as daemon ...
    Starting topexporterd as daemon ...
    Starting topfilterd as daemon ...
    Starting topmapperd as daemon ...
    Starting topondeliveryd as daemon ...
    Starting topreminderd as daemon ...
    Starting topcommsd as daemon ...
    Starting toppoderd as daemon ...

    $ topctrl stop
    Stopping toploaderd ...
    OK
    Stopping topexporterd ...
    OK
    Stopping topfilterd ...
    OK
    Stopping topmapperd ...
    OK
    Stopping topondeliveryd ...
    OK
    Stopping topreminderd ...
    OK
    Stopping topcommsd ...
    OK
    Stopping toppoderd ...
    OK
