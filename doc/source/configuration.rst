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
    #      00000000011111111
    #      12345678901234567
    TOLP = 00010000000001011
    TOLF = 00010110000001011
    TOLI = 10001000000001011

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
