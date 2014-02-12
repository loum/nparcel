.. Toll Parcel Portal B2C Configuration Items

.. toctree::
    :maxdepth: 2

.. _config_items:

Configuration Items
===================

Conditions Map
--------------
The conditions map is a Business Unit based binary-based, boolean lookup
that can alter the business logic and processing behaviour.

The conditions map is delimited in the configuration file by the
``[conditions]`` section.  A typical setting is as follows::

    [conditions]
    #      000000000111111111
    #      123456789012345678
    TOLP = 000100000000010110
    TOLF = 000101100000010110
    TOLI = 100010000000010110

Each column in the conditions maps string has semantic and is further
detailed here.

POD File Processing
+++++++++++++++++++

Signature file ``*.ps`` and ``*.png`` variants can selectively be sent to
the Business Units as a Proof of Delivery artefact and / or archived
with the Toll Parcel Portal system::

    # Pos 04: 0 do not send .ps files
    #         1 send .ps files
    # Pos 05: 0 do not send .png files
    #         1 send .png files
    ...
    # Pos 16: 0 do not archive .ps files
    #         1 archive .ps files
    # Pos 17: 0 do not archive .png files
    #         1 archive .png files

.. _sc4_template_selection:

Service Code 4 Template Selection
+++++++++++++++++++++++++++++++++

Service Code 4 job records can selectively use either the default ``body``
comms templates or the ``delay`` variant::

    # Pos 12: 0 use default loader comms template if service_code 4
    #         1 use delayed pickup comms template if service_code 4

.. _primary_elect_ondelivery:

Primary Elect On Delivery Comms
+++++++++++++++++++++++++++++++

Service Code 3 deliveries within Toll Parcel Portal have immediate
comms suppressed during the initial T1250 load (this is hard-wired into the
code base).  Instead, the middleware components interrogate alternate
interfaces to establish when the parcel has been delivered to the
Alternate Delivery Point.  This feature can be enabled on a per Business
Unit basis::

    # Pos 14: 0: disable Primary Elect notifications (On Delivery)
    #         1: enable Primary Elect notifications (On Delivery)

.. _sc4_ondelivery_bu_ids:

Service Code 4 On Delivery Comms Business IDs List
++++++++++++++++++++++++++++++++++++++++++++++++++

Service Code 4 deliveries within Toll Parcel Portal could have immediate
comms suppressed during the initial T1250 load.  Instead, the middleware
components interrogate alternate interfaces to establish when the parcel
has been delivered to the Alternate Delivery Point.  This feature can be
enabled on a per Business Unit basis::

    # Pos 15: 0: disable Service Code 4 on delivery notification (On Delivery)
    #         1: enable Service Code 4 on delivery notifications (On Delivery)
