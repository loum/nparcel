.. Nparcel B2C Environment Initialisation

.. toctree::
    :maxdepth: 2

Environment Initialisation
==========================

The Nparcel B2C software package is available to all system users.  However,
the environment needs to be initialised and configured for any of the
functionality to be useful.

Fresh Install
-------------

The ``npinit`` command creates the required directory structure and places
the required templates and configuration files in the default location.

.. _npinit-usage:

``npinit`` Usage
++++++++++++++++

::

    usage: npinit [options]
    
    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity
      -d, --dry             dry run - show what would have been done
      -c CONFIG, --config=CONFIG
                            override default config

``npinit`` with the dry flag is a useful starting point as it will only
display to the terminal the files and directories that will be required::

    $ npinit -d
    Logging verbosity set to "INFO" level
    Processing dry run True
    Starting npinit ...
    Preparing environment in "/home/guest/.nparceld"
    Copying "/usr/lib/python2.4/site-packages/nparcel/conf/init.conf.0.12"
    ...

``npinit`` will create the base directory structure in the ``.nparceld``
directory off the current user's home directory.

Keys Files at a Glance ...
++++++++++++++++++++++++++
As of release 0.12, the required directory structure is as follows::

    $ tree .nparceld/
    .nparceld/
    |-- conf
    |   |-- init.conf
    |   |-- init.conf.0.12
    |   |-- log.conf.0.12
    |   |-- nparceld.conf.0.12
    |   `-- npftp.conf.0.12
    `-- templates
        |-- email_body_html.t
        |-- email_err_body_html.t
        |-- email_err_pe_html.t
        |-- email_err_rem_html.t
        |-- email_html.t
        |-- email_message_q_err_html.t
        |-- email_message_q_warn_html.t
        |-- email_pe_html.t
        |-- email_rem_html.t
        |-- email_test_html.t
        |-- sms_body_xml.t
        |-- sms_pe_xml.t
        |-- sms_rem_xml.t
        |-- sms_test_xml.t
        |-- subject_body_html.t
        |-- subject_pe_html.t
        |-- subject_rem_html.t
        `-- subject_test_html.t

The main directories are:

* ``conf`` - Nparcel B2C configuration files
* ``templates`` - template file used by the Nparcel B2C comms facility

Set the Default Configuration
+++++++++++++++++++++++++++++
All commands use some form of configuration.  By default, the Nparcel B2C
components look for the default config at ``~.nparceld/nparceld.conf``::

    $ nploaderd status
    2013-10-08 17:26:04,266 CRITICAL:: Unable to locate config file:
    "/home/guest/.nparceld/nparceld.conf"

As a start, we can use the package-provided default::

    $ cd ~/.nparceld
    $ ln -s conf/nparceld.conf.0.12 nparceld.conf

From here we should get some sane information::

    $ nploaderd status
    nploaderd is idle

Set the Outbound FTP Configuration
++++++++++++++++++++++++++++++++++
The outbound FTP service has its own configuration file, ``npftp.conf``.
``npinit`` will provide a package version-based default but this needs to
be linked to the appropriate lcoation::

    $ cd ~/.nparceld
    $ ln -s conf/npftp.conf.0.12 npftp.conf

Provide Database Connection Details
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For the Nparcel B2C tools to be useful, you will need to add the database
instance connection details into the ``nparceld.conf`` configuration file.
By default, a new ``nparceld.conf`` configuration file features a section
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

The default settings for the condition map in release 0.12 are as follows::

    [conditions]
    #      000000
    #      123456
    TOLP = 000100
    TOLF = 000101
    TOLI = 111010

Adjust these to align with your environments requirements.

Supply the Esendex REST Credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If the Nparcel B2C comms facility is to be used, then supply the Esendex
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
Where possible, the new package ``nparceld.conf`` file tries to provide sane
defaults for the various facilities.  Adjust these to suit your requirements.

Enable the Logger Handlers
++++++++++++++++++++++++++
Log handlers manage the log files and need to be confgured::

    $ cd ~/.nparceld
    $ ln -s conf/log.conf.0.12 log.conf

Upgrade
-------
:ref:`npinit <npinit-usage>` can again be used to prepare the environment during a package
upgrade.  ``npinit`` will ensure that the required files (new or existing)
are put in their correct place.

Certain configuration files (such as ``nparceld.conf`` and ``npftp.conf``)
are not clobberred as to not override interface connection credentials.  In
this case, an additional manual step would be required to copy over the
connection credentials into the new, package-versioned configuration file and
relink.

``npinit`` arranges files into two categories:

* **unconditional** - existing files are clobberred to conform to the
  requirments of the package software

* **conditional** - copy file over only if it does not already exist

.. note::
    a backup of the existing file is made if the file to copy is flagged
    as **unconditional**

Verify Existing Options
+++++++++++++++++++++++
If your existing configuration arrangement features customisations, ensure
that you copy these over to the new ``nparceld.conf`` file.

The defaults are a good starting point but probably not what you require.
