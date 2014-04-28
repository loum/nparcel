.. B2C Delivery Partner Filter

.. toctree::
    :maxdepth: 2

Delivery Partner Agent Code Filtering
=====================================

The Toll Parcel Portal is able to extract alternate Delivery Partner
line items from the inbound T1250 files which are in turn on-forwarded
to that Delivery Partner's systems.


Agent Code Filtering Workflow
-----------------------------

T1250 files are picked up from the aggregator directory.  This directory is
defined by the ``aggregator`` configuration item::

    [dirs]
    ...
    aggregator = /data/nparcel/aggregate

Each T1250 EDI input stream can be configured to send their files
to the aggregator for futher processing.  This is controlled by the
``conditions`` map::

    ...
    # Pos 08: 0 do not copy T1250 files to the aggregator directory
    #         1 copy T1250 files to the aggregator directory
    ...
    [conditions]
    TOLI = 10001001000001011

The ``npfilterd`` daemon periodically polls the aggregator directory for
new files.  Valid Delivery Partner records are identified by an agent code
that starts with a pre-defined token.

Filtering rules per Alternate Delivery Partner are set in the Toll Parcel
Portal configuration file under the ``filters`` section::

    [filters]
    parcelpoint = P,R
    woolworths = U

This is read as **parcelpoint** Agent code search tokens are ``P`` and
``R``.  **woolworths** Agent code token is ``U``.

For example, if the agent is ``P001`` then the rule to ``P``.  Similarly,
``P0`` would also match.  In this case, the order of the list will take
precedence as to which token is matched first.

``npfilterd`` Usage
-------------------

``npfilterd`` can be configured to run as a daemon as per the following::

    $ npfilterd --help
    usage: npfilterd [options] start|stop|status
    
    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity
      -d, --dry             dry run - report only, do not execute
      -b, --batch           single pass batch mode
      -c CONFIG, --config=CONFIG
                            override default config
                            "/home/npprod/.nparceld/top.conf"
      -f FILE, --file=FILE  file to process inline (start only)

``npfilterd`` Configuration Items
---------------------------------

``npfilterd`` uses the standard ``top.conf`` configuration file.  The
following list details the required configuration options:

* ``aggregator_dirs`` (under the ``[dirs]`` section)

    list of inbound directories for ``npfilterd`` where comms event files
    are deposited for further processing

* ``staging_base`` (under the ``[dirs]`` section)

    outbound base directory.  Complete path is the concatenation of the
    ``staging_base``, Alternate Delivery Partner value from the ``filters``
    section and the token ``out`` 

* ``t1250_file_format`` (under the ``[files]`` section)

    regular expression based format string to match inbound T1250 EDI files
    for further processing

* ``filter_loop`` (under the ``[timeout]`` section)

    control filter daemon facility sleep period between aggregator
    directory checks

* ``support_emails`` (under the ``[email]`` section)

    comma separated list of email addresses to receive notifications in
    case things go wrong
