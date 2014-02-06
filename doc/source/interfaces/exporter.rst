.. Toll Parcel Portal B2C Exporter

.. toctree::
    :maxdepth: 2

Exporter
========

The Toll Parcel Portal exporter facility is responsible for identifying
parcels that have been picked up by the consumer and closing off the
item/job/job_item within the Toll Parcel Portal database.

Closing Off a Toll Parcel Portal Parcel Record
----------------------------------------------

Closing off includes:

* Identify the record to close in the Toll Parcel Portal database

* Locate the Proof of Delivery (signature or PoD) files

* Generate the Exporter report

* Bundle the Exporter report with the PoD

* Stage the Exporter output into the relevant Business Unit's outbound
  FTP directory

The trigger for a close-off event is a ``job_item`` record which has the
``pickup_ts`` column set (not ``NULL``) and ``extract_ts`` column not set
(``NULL``).  Here is an example of a close-off event
from the various upstream Business Units and extracts and loads parcel 
details into the Toll Parcel Portal in preparation for consumer pickup.

The list of Business Units supported include:
* Priority (``bu_id 1``)
* Fast (``bu_id 2``)
* IPEC (``bu_id 3``)

Exporter Report
---------------

Sample Exporter report::

    REF1|JOB_KEY|PICKUP_TIME|PICKUP_POD|IDENTITY_TYPE|IDENTITY_DATA|ITEM_NBR|AGENT_ID
    7179050166420|173357|2014-01-14 11:05:38|collected by home - simpson 2/2/2012|Manual POD|
    0000|00393403250082743890|Q081

``npexporterd`` Configuration Items
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``npexporterd`` uses the standard ``nparceld.conf`` configuration file to
control processing behaviour.  The following list details the required
configuration options:

* ``in``

    found under the ``[dirs]`` section, the ``in`` config setting defines
    the directories to search for new T1250 EDI files.  For example::

        in = /var/ftp/pub/nparcel/priority/in,/var/ftp/pub/nparcel/ipec/in

    These inbound directories typically align with the FTP inbound
    directory structure defined at :ref:`b2cftp`.

* ``archive`` (default ``/data/nparcel/comms``)

    found under the ``[dirs]`` section, ``archive`` defines where
    completed T1250 EDI files are deposited for archiving

* ``comms`` (default ``/data/nparcel/comms``)

    found under the ``[dirs]`` section, the comms outbound interface where
    comms event files are deposited for further processing

Enabling Comms
^^^^^^^^^^^^^^

Comms notification files can be enabled conditionally via the configuration
``condition_map`` setting::

    # Pos 02: 0 do not send email
    #         1 send email
    # Pos 03: 0 do not send SMS
    #         1 send SMS

As per the condition map descriptor, set the position item flags to ``1``
for the required communication facility.  For example::

    # TOLP condition map with comms disabled
    #      0000000001111
    #      1234567890123
    TOLP = 0001000000000

    # TOLP condition map with comms enabled
    #      0000000001111
    #      1234567890123
    TOLP = 0111000000000

.. note::

    Restart ``npexporterd`` for the configuration updates to take
    effect

``npexporterd`` usage
^^^^^^^^^^^^^^^^^^^^^

``npxporterd`` can be configured to run as a daemon as per the following::

    $ npexporterd -h
    usage: npexporterd [options] start|stop|status
    
    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity
      -d, --dry             dry run - report only, do not execute
      -b, --batch           single pass batch mode
      -c CONFIG, --config=CONFIG
                            override default config
                            "/home/npprod/.nparceld/nparceld.conf"
