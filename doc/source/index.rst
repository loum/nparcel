.. Nparcel B2C Replicator documentation master file

Nparcel B2C Replicator
======================

Overview
--------

The Nparcel B2C Replicator package presents an interface to the various Toll
divisions to upload missed parcel collection information into the Nparcel
portal at http://www.naparcel.com.au

Accepts a standard 1250 file of the consignments delivered to an Agent.
Once the consignment is collected by the consumer (or Toll as part of
aged / damaged process), a Proof of Delivery report file is sent back to
the freight management system with a copy of the associated signature file.

The Nparcel Replicator manages the following components:

* Loads T1250* files from upstream Business Units
* Sends customer notifications via email and/or SMS
* Extracts and delivers Proof of Delivery information

.. image:: _static/nparcel_overview.png
    :align: center
    :alt: Nparcel B2C Replicator overview

*The Nparcel B2C Replicator workflow*

Contents
--------
.. toctree::
    :maxdepth: 1

    modules/index.rst

Software Package Build
----------------------

Operations
----------

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
