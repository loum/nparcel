.. Toll Outlet Portal Middleware Configuration Items

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

.. _comms_control:

Comms Control
+++++++++++++

At the highest level, email and SMS comms can be controlled at a BU level::

    # Pos 02: 0 do not send email
    #         1 send email
    # Pos 03: 0 do not send SMS
    #         1 send SMS

.. _comms_service_code_based_control:

Comms Service Code-based Control
++++++++++++++++++++++++++++++++

By default, a Service Code value of NULL will trigger a ``body`` based
templated message (if :ref:`comms_control` is enabled).  However, comms can
also be controlled at the Service Code level by setting the following
flags::

    # Pos 09: 0 do not send comms if service_code 1
    #         1 send comms if service_code 1
    # Pos 10: 0 do not send comms if service_code 2
    #         1 send comms if service_code 2
    # Pos 11: 0 do not send comms if service_code 4
    #         1 send comms if service_code 4

.. _comms_sc4_template_control:

Comms Service Code 4 Template Control
+++++++++++++++++++++++++++++++++++++

Service Code 4 jobs are a special scenario whose comms could be suppressed
by the :ref:`loader` and triggered via the :ref:`on_delivery_trigger`
facility.  As such, the comms message context could be different and an
alternate template may be used instead of the default **body** template::

    # Pos 12: 0 use default loader comms template if service_code 4
    #         1 use delayed pickup comms template if service_code 4

If the flag is set, comms will be registered against the **delay** template.

.. _pod_file_processing:

POD File Processing
+++++++++++++++++++

Signature file ``*.ps`` and ``*.png`` variants can selectively be sent to
the Business Units as a Proof of Delivery artefact and / or archived
with the Toll Outlet Portal system::

    # Pos 04: 0 do not send .ps files
    #         1 send .ps files
    # Pos 05: 0 do not send .png files
    #         1 send .png files
    ...
    # Pos 16: 0 do not archive .ps files
    #         1 archive .ps files
    # Pos 17: 0 do not archive .png files
    #         1 archive .png files

.. _state_based_reporting:

State Based Reporting for the Exporter
++++++++++++++++++++++++++++++++++++++

::

    # Pos 06: 0 not state based reporting
    #         1 state based reporting

The Exporter can be configured to split of each parcel POD line item
into separate files that are delimited by state of origin.  For example::

    WA_VANA_REF_20140213120000.txt

.. note::

    This was a requirement for **Fast**

.. _suppress_pod:

Exporter Suppress POD for Primary Elect
+++++++++++++++++++++++++++++++++++++++

::

    # Pos 07: 0 do not suppress Primary Elect POD exports
    #         1 suppress Primary Elect POD exports

The Exporter can be configured to suppress the POD files if the parcel
was associated with a Primary Elect delivery scenario.

.. note::

    This was a requirement for **Fast**

.. _primary_elect_ondelivery:

Primary Elect On Delivery Comms
+++++++++++++++++++++++++++++++

Service Code 3 deliveries within Toll Outlet Portal have immediate
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

Service Code 4 deliveries within Toll Outlet Portal could have immediate
comms suppressed during the initial T1250 load.  Instead, the middleware
components interrogate alternate interfaces to establish when the parcel
has been delivered to the Alternate Delivery Point.  This feature can be
enabled on a per Business Unit basis::

    # Pos 15: 0: disable Service Code 4 on delivery notification (On Delivery)
    #         1: enable Service Code 4 on delivery notifications (On Delivery)
