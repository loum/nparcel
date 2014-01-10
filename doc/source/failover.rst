.. Toll Parcel Portal B2C Failover

.. toctree::
    :maxdepth: 2

Failover
========

The current Toll Parcel Portal database arrangement is active/passive in
nature and requires manual intervention to failover.  As such, two separate
configuration files are required:

* Prod-aware DB config file (``~/.nparceld/nparceld.conf.prod``)

* DR-aware DB config file (``~/.nparceld/nparceld.conf.dr``)

Preparing for Failover
----------------------

Following a standard Toll Parcel Portal install, the ``nparceld.conf`` will
be pointing to the most recent package release version::

    $ tree ~/.nparceld
    .nparceld
    ...
    |-- nparceld.conf -> conf/nparceld.conf.0.22
    ...

We need to break this soft link and replace it with the **prod** variant::

    $ cd ~/.nparceld
    $ rm nparceld.conf
    $ ln -s conf/nparceld.conf.0.22 nparceld.conf.prod
    $ ln -s nparceld.conf.prod nparceld.conf
    $ tree ~/.nparceld
    .nparceld
    ...
    |-- nparceld.conf -> nparceld.conf.prod
    |-- nparceld.conf.prod -> conf/nparceld.conf.0.22
    ...

Finally, we need to copy ``nparceld.conf`` into the **dr** variant and
make the appropriate database adjustment::

    $ cp nparceld.conf nparceld.conf.dr

Edit the ``nparceld.conf.dr`` file and adjust the ``db`` section to point
to the DR database connection::

    [db]
    driver = FreeTDS
    host = SQLDBAUZ01
    database = Nparcel
    user = npscript
    password = <password>
    port =  1443

Perform a Failover
------------------

To failover to the DR instance, soft link the ``nparceld.conf`` file
to the **dr** instance::

    $ cd ~/.nparceld
    $ rm nparceld.conf
    $ ln -s nparceld.conf.dr nparceld.conf

.. note::

    All daemons must be restarted once the configuration file has been
    modified.
