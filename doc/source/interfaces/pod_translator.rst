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

``nppodd`` Configuration Items
------------------------------

``nppodd`` uses the standard ``nparceld.conf`` configuration file.  The
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

* ``pod_dirs``

    inbound directory location to look for exporter files to process

* ``out_dir``

    outbound directory to place transposed files

* ``file_formats``

    * ``file_formats``

    list of python-based regular expressions that represent the type of
    files that can be parsed by the POD translation facility when polling
    the ``pod_dirs`` directories.  For example ``.*_REF_\d{14}\.txt$``
    will filter out the file ``NSW_VANA_REF_20140213120000.txt``
