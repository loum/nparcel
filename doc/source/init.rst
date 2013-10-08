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
    Copying "/usr/lib/python2.4/site-packages/nparcel/conf/init.conf.0.11.1"
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
    |   |-- init.conf.0.11.1
    |   |-- log.conf.0.11.1
    |   |-- nparceld.conf.0.11.1
    |   `-- npftp.conf.0.11.1
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
    $ ln -s conf/nparceld.conf.0.11 nparceld.conf

From here we should get some sane information::

    $ nploaderd status
    nploaderd is idle

Enable the Logger Handlers
++++++++++++++++++++++++++
Log handlers manage the log files and need to be confgured::

    $ cd ~/.nparceld
    $ ln -s conf/log.conf.0.11 log.conf

