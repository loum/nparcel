.. Toll Outlet Portal Middleware POD Archiving

.. toctree::
    :maxdepth: 2

.. _pod_archiving:

Proof of Delivery Archiving
===========================

The Toll Outlet Portal currently manages POD archiving of files from the
Portal itself and from ParcelPoint.

The Toll Outlet Portal POD information is a unique database (``jobitem``
table) primary key integer value.  For example::

    193433.ps
    193433.png

The Portal will then generate a ``PNG`` and ``PS`` variant of the POD
signature and present these to the :mod:`top.exporter` interface for
further processing.

ParcelPoint use an alpha-numeric variant filename but also produce
both ``PNG`` and ``PS`` formats.  For example::

    P3019BQ-0000SHP2.ps
    P3019BQ-0000SHP2.png

In both cases, the exporter will attempt the archive the POD files
during the :mod:`top.exporter` process.

POD File Indexing and Distribution
----------------------------------

In order to produce an even distribution of POD files across the server
filesystem, a hash value is created to produce a unique, evenly formatted
target.  The hash value is based on an md5 digest that produces a 32-byte
hexadecimal string.  The string is further split into 4 x 8-byte
strings that produce a 4-leaf directory structure.

.. note::

    Both ``PNG`` and ``PS`` files are stored in the generated directory

For example, a POD key value ``193433`` will generate the directory path
list::

    ['73b0b66e', '5dfe3567', '82ec56c6', 'fede538f']

This will produce the following directory path::

    73b0b66e/5dfe3567/82ec56c6/fede538f

``toppod`` Usage
----------------

``toppod`` is a CLI-based tool that can present a POD digest-based path::

    usage: toppod [options] <POD value>
    
    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity
      -d, --dry             dry run - report only, do not execute
      -b, --batch           single pass batch mode
      -c CONFIG, --config=CONFIG
                            override default config
                            "~/.top/top.conf"
    
As an example::

    $ toppod 193433
    Starting toppod inline (batch mode) ...
    path: /data/top/archive/signature/73b0b66e/5dfe3567/82ec56c6/fede538f

``toppod`` Configuration Items
------------------------------

The ``toppod`` utility uses the default ``top.conf`` file to parse
the ``archive_directory`` value.  POD files are archived to this location.

* ``archive_dir`` (default /data/top/archive)

.. note::

    ``archive_dir`` is the base archive directory used for
    archiving purposes.  The token ``signature`` is appended to the
    ``archive_dir`` base to separate it from other archived components
