.. Nparcel B2C Loader

.. toctree::
    :maxdepth: 2

Nparcel Loader
==============

The Nparcel loader facility manages ...

Nparcel Loader Workflow
-----------------------

``nploaderd`` Configuration Items
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``nploaderd`` uses the standard ``nparceld.conf`` configuration file.  The
following list details the required configuration options:

* ``comms`` (default ``/data/nparcel/comms``)

    The comms outbound interface where comms event files are
    deposited for further processing

* ``rest``

    The credentials and connection details required to interface to the
    Esendex SMS and email interfaces.  The config options include::

        sms_api = https://api.esendex.com/v1.0/messagedispatcher
        sms_user =
        sms_pw =
         
        email_api = https://apps.cinder.co/tollgroup/wsemail/emailservice.svc/sendemail
        email_user =
        email_pw =

* ``failed_email``

    Email recipient for loader failures notification alerts

* ``skip_days`` (default ``Sunday``)

    List of days to not send messages.  To avoid confusion,
    enter the full day name (Monday) separated by commas.

``nploaderd`` usage
^^^^^^^^^^^^^^^^^^^

``nploaderd`` can be configured to run as a daemon as per the following::

    $ nploaderd -h
    usage: nploaderd [options] start|stop|status
    
    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity
      -d, --dry             dry run - report only, do not execute
      -b, --batch           single pass batch mode
      -c CONFIG, --config=CONFIG
                            override default config
                            "/home/guest/.nparceld/nparceld.conf"
      -f FILE, --file=FILE  file to process inline (start only)

Errors
^^^^^^

