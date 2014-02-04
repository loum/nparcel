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

Futhermore, each T1250 input stream can be configured to send their files
to the aggregator for futher processing.  This is controlled by the
condition map::

    ...
    # Pos 08: 0 do not copy T1250 files to the aggregator directory
    #         1 copy T1250 files to the aggregator directory
    ...
    [conditions]
    TOLI = 10001001000001011

The ``npfilterd`` daemon periodically polls the aggregator directory for
new files.  Valid Delivery Partner records are identified by an agent code
that starts with a pre-defined token.

Filtering rules are a list of tokens that can be set in the Toll Parcel
Portal configuration file under the ``filter`` section::

    [filter]
    ...
    filtering_rules = P,R

For example, if the agent is ``P001`` then the rule to ``P``.  Similarly,
``P0`` would also match.  In this case, the order of the list will take
precedence as to which token is matched first.

``npfilterd`` Configuration Items
---------------------------------

``npfilterd`` uses the standard ``nparceld.conf`` configuration file.  The
following list details the required configuration options:

* ``aggregator`` (default ``/data/nparcel/aggregate``)

    The ``npfilterd`` inbound interface where comms event files are
    deposited for further processing

* ``staging_base`` (default /var/ftp/pub/nparcel)

    outbound base directory.  Complete path is the concatenation of the
    ``staging_base``, ``customer`` and the token ``out`` 

* ``filters_loop`` (default 30 (seconds))

    Control filter daemon facility sleep period between aggregator
    directory checks

* customer

    context of outbound processing (default ``parcelpoint``)

* filtering_rules

    list of tokens to match against the start of the agent code field

``npfilterd`` usage
-------------------

``npcommsd`` can be configured to run as a daemon as per the following::

    $ npfilterd --help
    usage: npfilterd [options] start|stop|status
    
    options:
      -h, --help            show this help message and exit
      -v, --verbose         raise logging verbosity
      -d, --dry             dry run - report only, do not execute
      -b, --batch           single pass batch mode
      -c CONFIG, --config=CONFIG
                            override default config
                            "/home/npprod/.nparceld/nparceld.conf"
      -f FILE, --file=FILE  file to process inline (start only)
