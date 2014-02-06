.. Toll Parcel Portal On Delivery Comms Trigger

.. toctree::
    :maxdepth: 2

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

``npondelivery`` Configuration Items
------------------------------------

The ``npondeliveryd`` utility uses the default ``nparceld.conf`` file to
control processing workflows.

* ``report_in_dir``

    found under the ``[primary_elect]`` section,  ``report_in_dir`` is the
    Delivery Report inbound directory (default ``/data/nparcel/tcd``)

* ``tcd_filename_format``

    found under the ``[primary_elect]`` section, ``tcd_filename_format`` is
    the TCD Delivery Report filename format as expressed as a Python
    regular expression string (default ``mts_delivery_report_\d{14}\.csv``)
