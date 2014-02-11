.. Toll Parcel Portal On Delivery Comms Trigger

.. toctree::
    :maxdepth: 2

.. _on_delivery_trigger:

On Delivery Comms Trigger
=========================

In addition to the "Sorry we missed you ..." scenario that redirects
parcels to an Alternate Delivery Point if the consumer is not present
at the nominated address to accept delivery, the Toll Parcel Portal
supports an On Delivery comms trigger.  In this case, a special
delivery type will suppress comms notifications during the initial
:mod:`nparcel.loader` until which time that the parcel was physically
delivered to the Alternate Delivery Point.  The delivery types that
require this additional level of processing are:

* **Primary Elect** - where the consumer is able to nominate an
  Alternate Delivery Point from where they will pick up the parcel

* **Priority Transfer out to V123 (Service Code 4)**

On Delivery comms trigger is processed by the ``npondeliveryd`` daemon.
The ``npondeliveryd`` daemon polls alternate interfaces to identify
a delivery event at the Alternate Delivery Point.

The alternate interfaces used include:

* **TransSend**

* **TCD**

.. note::

    MTS was deprecated as part of release 0.28

Comms Templates
---------------

The delivery scenario (either **Primary Elect** or **Priority Transfer** out
to V123) will determine the type of comms template to use.  Primary Elect is
standard and simply uses the ``pe`` template.  For example, if
``job_item.id`` 12345 triggers an On Delivery event, then (if configured)
the comms events files generated include::

    $ ls -1 /data/nparcel/comms
    $ email.12345.pe
    $ sms.12345.pe

**Priority Transfer out to V123** defaults to the standard ``body``
template.  However, as of *release 0.26* is behavior can be altered
to use the ``delay`` template as detailed in the
:ref:`sc4_template_selection`

``npondeliveryd`` Usage
-----------------------

``npondeliveryd`` is a CLI-based daemoniser that controls the
On Delivery comms trigger process::

    $ npondeliveryd -h
    usage: npondeliveryd [options] start|stop|status
    
    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity
      -d, --dry             dry run - report only, do not execute
      -b, --batch           single pass batch mode
      -c CONFIG, --config=CONFIG
                            override default config
                            "/home/npprod/.nparceld/nparceld.conf"
    -f FILE, --file=FILE  file to process inline (start only)

``npondeliveryd`` Configuration Items
-------------------------------------

The ``npondeliveryd`` utility uses the default ``nparceld.conf`` file to
control processing workflows.

.. note::
    all configuration settings are found under the ``[primary_elect]``
    section unless otherwise specified

* ``tcd_in`` (under the ``[dirs]`` section)

    TCD Delivery Report inbound directory (default ``/data/nparcel/tcd``)

* ``tcd_filename_format``

    TCD Delivery Report filename format as expressed as a Python
    regular expression string (default ``TCD_Delivery_\d{14}\.DAT``)

* ``file_cache_size``

    number of date-ordered TCD files to load during a
    processing loop.  Additonal files are deleted from the system

* ``comms`` (under the ``[dirs]`` section)

    directory where comms files are staged for further processing

* ``ondelivery_loop``

    time (seconds) between ``ondeliveryd`` processing iterations

* ``pe_comms`` (set via the ``[conditions]`` map position 14)

    enable/disable Primary Elect notifications (On Delivery)

* ``sc4_comms_ids`` (set via the ``[conditions]`` map position 15)

    enalbe/disable Service Code 4 on delivery notification (On Delivery)

* ``db`` (the actual ``[db]`` section)

    Toll Parcel Portal database connectivity information.  A typical
    example is::

        [db]
            driver = FreeTDS
            host = SQVDBAUT07
            database = Nparcel
            user = npscript
            password = <passwd>

* ``transsend_db`` (the actual ``[transsend_db]`` section)

    TransSend database connectivity information.  A typical example is::

        [transsend_db]
            host = siedbdop01
            user = NPARCEL
            password = <password>
            port = 1521
            sid = TRCOPDOV

* ``uncollected_day_range``

    number in days to include in the ``jobitems.uncollected_jobitems_sql``
    query uncollected_day_range (default 14.0)

* ``delivered_header`` (under the ``[transsend]`` section)

    string that represents the TransSend column header name for a delivered
    item (default ``latest_scan_event_action``)

* ``delivered_event_key`` (under the ``[transsend]`` section)

    string that represents a delivered event (default ``delivered``)

* ``scan_desc_header`` (under the ``[transsend]`` section)

    the scanned description column header in TransSend
    (default ``latest_scanner_description``)

* ``scan_desc_keys`` (under the ``[transsend]`` section)

    list of scan_desc_header tokens to compare against
    (default ``IDS – TOLL FAST GRAYS ONLINE``)
