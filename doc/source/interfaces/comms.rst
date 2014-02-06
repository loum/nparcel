.. B2C Comms

.. toctree::
    :maxdepth: 2

Comms
======

The Toll Parcel Portal comms facility manages comsumer notifications.
Notifications are provided via email and SMS.

The types of consumer notifications supported by the Comms facility are:

* **"Sorry we missed you ..."**

    Triggered when loaded into the Toll Parcel Portal database

* **Reminders**

    Triggered if the parcel has not been picked up a pre-defined period
    after the initial notification has been sent

* **Primary Elect**

    Triggered *after* load into the Toll Parcel Portal database and
    verification has been obtained that the parcel has been delivered to
    the ADP.  Verification is typically provided via an alternate interface
    (for example, TCD report or TransSend)

Comms Workflow
--------------

.. note ::

    Refer to the individual Toll Parcel Portal B2C sub-systems for a more
    detailed analysis of the business rules that trigger a comms event.

In general, the various subsystems generate a comms event by providing an
appropriately constructed file to the comms module interface.

.. note::

    The comms interface is a simple directory structure
    (default ``/data/nparcel/comms``)

Comms event files are processed by the ``npcommsd`` daemon process.

Comms Event Files
^^^^^^^^^^^^^^^^^

A comms event is defined by a simple, empty file which conforms to a defined
filename convention.  In general, a comms event file is formatted as
follows::

    <action>.<jobitem.id>.<template>

* **<action>**

    The communication medium (either ``email`` or ``sms``)

* **<jobitem.id>**

    The integer value representing the ``jobitem.id`` column in the
    Toll Parcel Portal database

* **<template>**

    The template used to built the message

.. note..

    Comms event files are case sensitive

``npcommsd`` Configuration Items
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``npcommsd`` uses the standard ``nparceld.conf`` configuration file.  The
following list details the required configuration options:

* ``comms`` (default ``/data/nparcel/comms``)

    The ``npcommsd`` inbound interface where comms event files are
    deposited for further processing

* ``comms_loop`` (default 30 (seconds))

    Control comms daemon facility sleep period between comms event file
    checks.

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

    Email recipient for comms failures notification alerts

* ``skip_days`` (default ``Sunday``)

    List of days to not send messages.  To avoid confusion,
    enter the full day name (Monday) separated by commas.

* ``send_time_ranges`` (``default 08:00-19:00``)

    Time ranges when comms *can* be sent.  Use 24 hour format and ensure
    that the times are day delimited.  Ranges must be separated with a
    hyphen '-' and use format HH:MM.  Multiple ranges are separated with
    commas.

* ``comms_queue_warning`` (default 100)
    Threshold limit that will invoke a warning email to support if breached.
    A typical notification email is as follows:

.. image:: ../_static/comms_warning.png
    :align: center
    :alt: Toll Parcel Portal B2C Comms Queue Threshold Warning
        

* ``comms_queue_error`` (default 1000 )
    Threshold limit that will invoke an error email to support if breached
    and terminate the ``npcommsd`` daemon.

``npcommsd`` usage
^^^^^^^^^^^^^^^^^^

``npcommsd`` can be configured to run as a daemon as per the following::

    $ npcommsd -h
    usage: npcommsd [options] start|stop|status
    
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

There are a few places where things can go wrong:

1. Invalid email/SMS construct. For example, if number does not start with "04" then it is not a mobile
2. Network exception
3. Esendex response

1 and 2 should be covered in the code base.  For 3, Esendex return their
own response:

**SMS**::

    "<?xml version="1.0" encoding="utf-8"?><messageheaders batchid="fc8f4a85-a973-4d66-9f37-a1c73afabf7f" xmlns="http://api.esendex.com/ns/"><messageheader uri="https://api.esendex.com/v1.0/messageheaders/c321a89c-5ec7-4946-85f3-fb4ebaad07ab" id="c321a89c-5ec7-4946-85f3-fb4ebaad07ab" /></messageheaders>"

**Email**::

    "<string xmlns="http://schemas.microsoft.com/2003/10/Serialization/">[{"email":"lou.markovski@tollgroup.com","status":"sent","_id":"9ceb663a68e34ce0a178d928289c8bc0","reject_reason":null}]</string>

In both cases, these are string representations of some kind of structured
data.  For example, the SMS is XML based whereas the Email looks like a
bit of JSON.  For both email and SMS Esendex responses, the Comms module
simply logs the returned values.

.. note::

  The Esendex response is only the first-hop return value from their own
  interface.  We do not have any visibility of the interaction that
  Esendex have with the Telcos.  Therefore, there is still not a 100%
  guarantee that the message transfers were actually successful.  However,
  Esendex does provide another interface which we can query to verify the
  status of the message ID that they provide in their responses.  This is
  currently a manual process on a "need to know" basis.

When an error is detected in code, all efforts are made to alert the
Toll Parcel Point support email.  A sample failure email construct is as
follows:

    .. image:: ../_static/comms_failure.png
        :align: center
        :alt: Toll Parcel Point B2C Comms Failure Alert Email
