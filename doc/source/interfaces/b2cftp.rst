.. B2C FTP

.. toctree::
    :maxdepth: 2

B2C FTP
=======
The Toll Parcel Portal B2C Exporter produces Proof of Delivery (POD)
report files that need to be returned to the relevant Business Units to
complete the end-to-end process flow.  POD reports are accompanied by
signature files.

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

ParcelPoint Integration
-----------------------

As of *version 0.20*, the Toll Parcel Portal FTP sub-system provides an
interface to `ParcelPoint <http://parcelpoint.com.au>`_

Toll Parcel Portal FTP delivers T1250 files and receives POD report
files from ParcelPoint.

Configuration
-------------

Business Unit Interfaces
++++++++++++++++++++++++
The configuration file for the outbound FTP facility is ``npftp.conf``.  The
default location for the file is::

    ~/.nparceld/conf/npftp.conf

A typical entry for *Priority* is shown below::

    [ftp_priority]
    direction = outbound
    host = localhost
    port = 21
    user = priority
    password = <password>
    source = /var/ftp/pub/nparcel/priority/out
    filter = VIC_VANA_REI_\d{14}\.txt$
    target = in
    pod = yes

Key items in the configuration are:

* FTP interface sections (for example, ``[ftp_priority]``) need to start
  with ``ftp_`` to be accepted as a valid interface

* ``host``, ``port``, ``user``, ``password`` and ``target`` are the
  components of the remote FTP server

* ``source`` is the Business Unit Exporter staging area interface

*new in version 0.20*

* ``direction`` determines transfer flow relative to the Toll Parcel Portal
  FTP server.  Supported values include ``inbound`` and ``outbound``
  (default ``outbound``)

* ``filter`` a Python regular expression that can be used to filter files

* ``pod`` flags the transfer as POD-type files.  POD files require an
  additional sub-transfer or POD signature files that are associated
  with a particular POD report file

ParcelPoint Configuration
+++++++++++++++++++++++++
The Toll Parcel Portal inbound/outbound concept is somewhat reversed
for the ParcelPoint outbound interface.  In this case, *outbound* is the
delivery of T1250 files to ParcelPoint.  The ``source`` configuration 
item is the name of the *local* directory to search for T1250 files to
deliver.  Similarly, ``target`` is the remote server directory to send
files to.  Again, the context of the definitions is relative to the Toll
Parcel Portal system.

.. note::

    T1250 file outbound transfer support is available as of *version 0.20*

The following configuration will *send* T1250 to ParcelPoint::

    [ftp_parcelpoint_out]
    direction = outbound
    host = ftp.parcelpoint.com.au
    port = 21
    user = tollftp
    password = <password>
    source = /var/ftp/pub/nparcel/parcelpoint/out
    filter = T1250_TOL[PFI]_\d{14}\.txt$
    target = /incoming/nparcel
    proxy = proxy.toll.com.au

New configuration items relative to *outbound* transfers include:

* ``proxy`` specifies the name of the FTP proxy server.  This item
  is required in a firewalled environment such as Toll

The following configuration will *retrieve* POD report files from
ParcelPoint::

    [ftp_parcelpoint_in]
    direction = inbound
    host = ftp.parcelpoint.com.au
    port = 21
    user = tollftp
    password = Xw87gwJF
    source = /outgoing/events
    filter = .*_VANA_RE[PFI]_\d{14}\.txt$
    target = /var/ftp/pub/nparcel/parcelpoint/in
    pod = yes
    delete = yes
    partial = yes
    proxy = proxy.toll.com.au

New configuration items relative to *inbound* transfers include:

* ``delete`` remove the remote file upon successful transfer

* ``partial`` transfer the remote file into a temporary file on the
  local directory.  When set, the file under transfer will feature a
  ``.tmp`` extension locally

Archive Directory
+++++++++++++++++
The outbound FTP facility will attempt to archive files upon successful
transfer if the ``archive`` configuration option is defined::

    [dirs]
    archive = /data/nparcel/archive/ftp

An attempt will be made to create the archive directory if it does not exist.

The ``archive`` option is part of the **npftp.conf** ``dirs`` section

To disable FTP archiving: simply comment out the ``archive`` option as
below::

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

    10,25,40,55 * * * * /usr/local/bin/npftp

.. note::

    The above crontab entry will send notifications at 15 minute intervals
