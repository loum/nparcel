.. Toll Outlet Portal Middleware Failover

.. toctree::
    :maxdepth: 2

Failover
========

The current Toll Outlet Portal database arrangement is active/passive in
nature and requires manual intervention to failover.  As such, two separate
configuration files are required:

* Prod-aware DB config file (``~/.top/top.conf.prod``)

* DR-aware DB config file (``~/.top/top.conf.dr``)

Preparing for Failover
----------------------

Following a standard Toll Outlet Portal install, the ``top.conf`` will
be pointing to the most recent package release version::

    $ tree ~/.top
    .top
    ...
    |-- top.conf -> conf/top.conf.0.22
    ...

We need to break this soft link and replace it with the **prod** variant::

    $ cd ~/.top
    $ rm top.conf
    $ ln -s conf/top.conf.0.22 top.conf.prod
    $ ln -s top.conf.prod top.conf
    $ tree ~/.top
    .top
    ...
    |-- top.conf -> top.conf.prod
    |-- top.conf.prod -> conf/top.conf.0.22
    ...

Finally, we need to copy ``top.conf`` into the **dr** variant and
make the appropriate database adjustment::

    $ cp top.conf top.conf.dr

Edit the ``top.conf.dr`` file and adjust the ``db`` section to point
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

To failover to the DR instance, soft link the ``top.conf`` file
to the **dr** instance::

    $ cd ~/.top
    $ rm top.conf
    $ ln -s top.conf.dr top.conf

.. note::

    All daemons must be restarted once the configuration file has been
    modified.
