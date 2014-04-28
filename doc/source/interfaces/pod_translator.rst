.. B2C POD Translator

.. toctree:
    :maxdepth: 2

POD Translator
==============

Currently, the ParcelPoint POD ``*.txt`` and ``*.ps`` files are returned
to Toll Fast in a format that is incompatible with the FAST systems. A
typical ParcelPoint format is ``P1019BQ-0000P5C2.ps``.

The business rules required by FAST include:

* only POD files with 11 numeric characters in the filename are supported

* the naming convention for the ``*.txt`` will remain the same.  For
  example, ``NSW_ VANA_REF_20131203103942.txt``

* the naming convention for the ``*.ps`` file will change to a numeric
  sequence <= to 11 numeric characters in length

POD Translator Workflow
-----------------------

The POD Translator facility is managed by the ``nppoderd`` daemon.  The
solution was designed to sit in between the ParcelPoint report inbound
directory and the Business Unit report outbound directory.  As such,
required configuration parameters include the inbound
:ref:`pod_dirs <pod_dirs>` and the outbound :ref:`out_dir <out_dir>`.

In general, ``nppoderd`` will source files from :ref:`pod_dirs <pod_dirs>`
and deposit translated files to :ref:`out_dir <out_dir>`.

The Token Generator
^^^^^^^^^^^^^^^^^^^

The POD Translator features a customised token generator that provides a
unique, unambiguous numeric representation for a POD identifier.

.. note::

    Unique and unambiguous only if a single instance of ``nppoderd``
    is active.
        
The token generation algorithm is based on seconds since epoch which
maintains a natural counter with a decisecond value appended.  Furthermore, the leading interger value is replaced with a ``0`` (zero) to prevent
conflict with the existing ``job_item.id`` signature file naming convention.
A typical example of a new token is ``03971803521``.

.. note::

    By replacing the leading, most significant integer value from the epoch
    counter we are effectively limiting the capacity of the number of
    token values available to us.  As such, if we are using this solution
    beyond 2033-05-18 13:33:20 UTC we may have a problem.

Token generation is based on current time.

Token Substitution
^^^^^^^^^^^^^^^^^^

With the new token generated, ``nppoderd`` will attempt to substitute the
``JOB_KEY`` column value in the report file and the names of the signature
files.  For example, if the original files in the source directory
include::

    $ ls -1 /var/ftp/pub/nparcel/parcelpoint/in/
    P3014R0-00007388.ps
    P3014R0-00007399.ps
    VIC_VANA_REP_20131121065550.txt

and the contents of the report file include::

    Ref1|JOB_KEY|PICKUP_TIME|PICKUP_POD|IDENTITY_TYPE|IDENTITY_DATA|ITEM_NBR
    ARTZ077895|P3014R0-00007388|2013-11-21 06:15:51|Lou Markovski|PHOTO|PPNT|00393403250082816686
    ARTZ077895|P3014R0-00007399|2013-11-21 06:15:51|Lou Markovski|PHOTO|PPNT|00393403250082816687

the result will be::

    $ ls -1 /var/ftp/pub/nparcel/fast/out/
    03971803521.ps
    03971803522.ps
    QLD_VANA_REF_20131121065550.txt

with translated report file contents::

    Ref1|JOB_KEY|PICKUP_TIME|PICKUP_POD|IDENTITY_TYPE|IDENTITY_DATA|ITEM_NBR
    ARTZ077895|03971803521|2013-11-21 06:15:51|Lou Markovski|PHOTO|PPNT|00393403250082816686
    ARTZ077896|03971803522|2013-11-21 06:15:51|Lou Markovski|PHOTO|PPNT|00393403250082816687

.. note::

    Source report filename will remain the same.

Archiving
^^^^^^^^^

At the end of successful processing, the original file will be archived
as per the :ref:`archive_dir <archive_dir>` setting.  By default, this
base directory will have ``podtranslated`` appended to it.

``nppoderd`` Usage
------------------

``nppoderd`` can be run as a daemon as per the following::

    $ nppoderd --help
    usage: nppoderd [options] start|stop|status
    
    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity
      -d, --dry             dry run - report only, do not execute
      -b, --batch           single pass batch mode
      -c CONFIG, --config=CONFIG
                            override default config
                            "/home/npprod/.nparceld/top.conf"
      -f FILE, --file=FILE  file to process inline (start only)

``nppoderd`` Configuration Items
--------------------------------

``nppoderd`` uses the standard ``top.conf`` configuration file.  The
following list details the required configuration options:

.. note::

    all configuration settings are found under the ``[pod]`` section
    unless otherwise specified

* ``prod`` (under the ``[environment]`` section)

    hostname of the production instance.  This is used to flag **TEST**
    comms messages

* ``support`` (under the ``[email]`` section

    comma separated list of email addresses to receive notifications
    in case things go wrong

.. _pod_dirs:

* ``pod_dirs``

    inbound directory location to look for exporter files to process

.. _out_dir:

* ``out_dir``

    outbound directory to place transposed files

* ``file_formats``

    list of python-based regular expressions that represent the type of
    files that can be parsed by the POD translation facility when polling
    the ``pod_dirs`` directories.  For example ``.*_REF_\d{14}\.txt$``
    will filter out the file ``NSW_VANA_REF_20140213120000.txt``

.. _archive_dir:

* ``archive_dir`` (under the ``[dirs]`` section)

    base directory where working files are archived to
