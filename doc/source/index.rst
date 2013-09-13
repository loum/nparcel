.. Nparcel B2C Replicator documentation master file

Nparcel Replicator
==================

Accepts a standard 1250 file of the consignments delivered to a newsagent.
Once the consignment is collected by the consumer or Toll as part of
aged / damaged process, a file is sent back to the freight management
system with the POD collected details and electronic signature file.

The Nparcel Replicator manages the following components:

* Loads T1250* files from upstream BU's
* Sends customer notifications via email and/or SMS
* Extracts and delivers Proof of Delivery information

Nparcel Modules
===============

.. toctree::
    :maxdepth: 2

    config.rst
    parser.rst
    dbsession.rst

    loaderdaemon.rst
    loader.rst

    emailer.rst
    exporterdaemon.rst
    exporter.rst

    reporter.rst

    rest.rst
    restemailer.rst
    restsmser.rst

    ftp.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
