.. Toll Outlet Portal Middleware On Delivery Notifications

.. toctree::
    :maxdepth: 2

.. _primary_elect:

Primary Elect
=============
*New in version 0.14*

Primary Elect is a service provided to the customer that allows them
to nominate the Alternate Delivery Point from where they can pick up
their parcels.

Primary Elect jobs differ from the normal Toll Outlet Portal flow in that
the jobs are not triggered by a failed delivery event.  Instead, jobs are
sent directly from the vendor (for example, Grays Online)

.. note::

    Current arrangement is a short-term solution to enable the Primary
    Elect service option whilst the various Business Units update their
    systems to accommodate such requests in the future.

.. _primary_elect_workflow:

Primary Elect Workflow
----------------------

Raw WebMethods T1250 Files -- GIS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Since the various Business Units do not support Primary Elect jobs,
Toll Outlet Portal receives a direct feed from the GIS-prepared WebMethods
interface.  Toll Outlet Portal uses the :mod:`top.mapper` middleware
component to translate the WebMethods format into typical T1250 EDI files.

The :mod:`top.mapper` workflow starts with the ``topmapperd`` script.
First, ``topmapperd`` will check for WebMethods raw ``*.dat`` files and
attempts to translated these into T1250 EDI format.  From here, the
translated T1250 files are deposited into the corresponding Business Unit
inbound FTP resource directories where they enter into the normal Toll
Outlet Portal workflow.

.. note::

    Translated T1250 EDI files that are processed by ``toploaderd``
    **will not** generate comms files (Service Code ``3`` scenario)

Some notable functionality provided by the translation process:

* pre-populates the *Service Code* field (offset 842) with the value ``3``
  which represents a Primary Elect job type

``topmapperd`` Configuration Items
**********************************

:mod:`top.mapper` uses the standard ``top.conf`` configuration
file to define the WebMethods interface.  The following list details
the required configuration options:

.. note::

    All configuration settings are found under the ``[primary_elect]``
    section unless otherwise specified

* ``mapper_loop``

    Control mapper daemon facility sleep period between inbound file checks.
    Default 30 (seconds)

* ``pe_customer``

    upstream provider of the T1250 files.  Default "gis"

* ``mapper_in``

    Found under the ``[dirs]`` section, inbound file from GIS are transfered
    via FTP into the this directory.  ``mapper_in`` represents the FTP
    resource that files are deposited to and where ``topmapperd`` looks
    for files to process.  Default ``/var/ftp/pub/top/gis/in``

    .. note::

        As with the other FTP interfaces, the FTP resource needs to be
        created as per `these instructions <vsftpd.html>`_

* ``file_format``

    File format represents the filename structure to parse for Primary Elect
    inbound.  This was prepared during development so it may change later
    on.  Better to adjust it via config then in code.  Default
    ``T1250_TOL[PIF]_\d{14}\.dat``

* ``file_archive_string``

    Each T1250 should contain a YYYYMMDD sequence that defines date.  This
    is used by the archiver.  The file_archive_string captures the regular
    expression grouping that defines the date.  Default
    ``T1250_TOL[PIF]_(\d{8})\d{6}\.dat``

* ``archive_dir`` (under the ``[dirs]`` section)

    Base directory where processed ``*.dat`` files are archived to.
    Directory is expanded on to capture context of current file.
    For example, if the source file is
    ``<ftp_base>/top/in/T1250_TOLI_20131011115618.dat`` then the
    archive target would be similar to
    ``<archive_dir>/gis/20131011/T1250_TOLI_20131011115618.dat``

* ``support`` (under the ``[email]`` section)

    comma separated list of email addresses to receive notifications
    in case things go wrong

``topmapperd`` Usage
********************

``topmapperd`` can be configured to run as a daemon as per the following::

    $ topmapperd -h
    usage: topmapperd [options] start|stop|status
    
    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity
      -d, --dry             dry run - report only, do not execute
      -b, --batch           single pass batch mode
      -c CONFIG, --config=CONFIG
                              override default config
                              "/home/npprod/.top/top.conf"
      -f FILE, --file=FILE  file to process inline (start only)

Primary Elect Nofitications
^^^^^^^^^^^^^^^^^^^^^^^^^^^
In a similar fashion to the ``topreminderd`` process, Primary Elect
consumer notifications are managed by a separate process,
:ref:`on_delivery_trigger`.  Here, the ``npondeliverd`` identifies all
Primary Elect jobs whose job items have not had their ``jobitem.notify_ts``
column set and cross references the connote/item number entries against
TransSend and TCD Fast Delivery Report.
