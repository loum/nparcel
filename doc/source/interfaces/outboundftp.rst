.. Nparcel B2C Inbound FTP

.. toctree::
    :maxdepth: 2

Outbound FTP
============
The Nparcel B2C Exporter produces Proof of Delivery (POD) report files
that need to be returned to the relevant Business Units to complete the
end-to-end process flow.  POD reports are accompanied by signature files.

The interface between the Exporter facility and the outbound FTP is
defined by the Exporter's ``staging_base`` configuraton option (under the
``dirs`` section).  This is also referred to as the *Exporter staging
directory*.

The staging directory is Business Unit-specific and branches off the
staging directory base.  For example, if the ``staging_base`` is defined
as ``/var/ftp/pub/nparcel`` the staging area for Priority will be
``/var/ftp/pub/nparcel/priority/out``.  In general, this can be represented
as::

    <staging_base>/<business_unit>/out

Configuration
-------------

Business Unit Interfaces
++++++++++++++++++++++++
The configuration file for the outbound FTP facility is ``npftp.conf``.  The
default location for the file is::

    ~.nparceld/conf/npftp.conf

A typical entry for Priority is shown below::

    [ftp_priority]
    host = localhost
    port = 21
    user = priority
    password = <password>
    source = /var/ftp/pub/nparcel/priority/out
    target = in

Key items in the configuration are:

* FTP interface sections (for example, ``[ftp_priority]``) need to start with
  ``ftp_`` to be accepted as a valid interface

* ``host``, ``port``, ``user``, ``password`` and ``target`` are the components
  of the remote FTP server

* ``source`` is the Business Unit Exporter staging area interface

Archive Directory
+++++++++++++++++
The outbound FTP facility will attempt to archive files upon successful
transfer if the ``archive`` configuration option is defined::

    [dirs]
    archive = /data/nparcel/archive/ftp

An attempt will be made to create the archive directory if it does not exist.

The ``archive`` option is part of the **npftp.conf** ``dirs`` section

To disable FTP archiving: simply comment out the ``archive`` option as below::

    [dirs]
    #archive = /data/nparcel/archive/ftp

``npftp`` Usage
---------------

::

    usage: npftp [options]
    
    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity
      -d, --dry             dry run - show what would have been done
      -c CONFIG, --config=CONFIG
                            override default config
                            "/home/lupco/.nparceld/npftp.conf"

``npftp`` has been designed to run as a batch process and can be executed
via cron with the following entry::

    0 55 * * * /users/npprod/npftp

.. note::

    Note the above crontab entry will send notifications at 55 minutes past
    every hour

