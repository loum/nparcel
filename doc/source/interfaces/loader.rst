.. Toll Parcel Portal B2C Loader

.. toctree::
    :maxdepth: 2

Loader
======

The Toll Parcel Portal loader facility accepts inbound T1250 EDI files
from the various upstream Business Units and extracts and loads parcel 
details into the Toll Parcel Portal in preparation for consumer pickup.

The list of Business Units supported include:
* Priority (``bu_id 1``)
* Fast (``bu_id 2``)
* IPEC (``bu_id 3``)

.. note::

    an additional upstream feed provided by GIS also provides T1250
    for the Primary Elect solution.  Refer to :ref:`primary_elect_workflow`

Loader Workflow
---------------

``nploaderd`` Configuration Items
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``nploaderd`` uses the standard ``nparceld.conf`` configuration file to
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

.. note:: Restart ``nploaderd`` for the configuration updates to take effect

Fine Tuning Comms via Service Code
**********************************

.. note::
    Service Code-level comms will only work if the comms facility has
    been enabled.

The context of T1250 line items can be altered based on the Service Code
value.  Similarly, Loader comms can be controlled at the Service Code level.

.. note::
    Primary Elect (Service Code 3) comms are never sent
    at the Loader level.

Service Code-level comms notification files can be enabled conditionally
via the configuration::

    # Pos 09: 0 do not send comms if service_code 1
    #         1 send comms if service_code 1
    # Pos 10: 0 do not send comms if service_code 2
    #         1 send comms if service_code 2
    # Pos 11: 0 do not send comms if service_code 4
    #         1 send comms if service_code 4

Selecting Templates
*******************

*New in version 0.18*

The Loader facility uses a default template for comms notifications.
However, Service Code 2 and 4-based T1250 records can use the alternate
``delay`` template.  This scenario represents alternate notifications
consistent with consumers electing to have their parcels delivered to
an Alternate Delivery Point for pickup.

Service Code 2 and 4 template control can be enabled conditionally
via the configuration condition_maps::

    # Pos 12: 0 use default loader comms template if service_code 4
    #         1 use delayed pickup comms template if service_code 4
    ...
    # Pos 18: 0 use default loader comms template if service_code 2
    #         1 use delayed pickup comms template if service_code 2

..note::

    Service Code 2 template selections was enables in version 0.28

Ignore Service Code 4
*********************

*New in version 0.18*

With future plans to trigger Service Code 4 comms *on delivery* we can
force the loader to ignore all Service Code 4 record types via the
configuration condition_map::

    # Pos 13: 0: do not ignore service_code 4
    #         1: ignore service_code 4

.. note::
    Once set, this setting overrides all other Service Code 4 related
    conditon_map items

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
