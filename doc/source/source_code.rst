.. B2C Middleware Source Code Repository and Packaging

B2C Middleware Source Code Repository and Packaging
===================================================

The Development Environment
---------------------------

The Toll Parcel Portal will run on any \*nix based system that runs Python
2.4 or greater.

If accessing the middleware source code for the first time, you will need to
meet the following list of dependencies in order to *pull* the code base,
test and build the package for deployment.

Git
^^^

If using an older version of RedHat/Centos (for example, version 5.*) you
may be missing ``git``.  This is presumably because CentOS 5 is based on
RHEL 5, which was released in 2007, before ``git`` was considered a mature
version control system.

Installation of ``git`` on RedHat/CentOS 5 requires the following pacakges::

    ========================================================================
    Package           Arch       Version              Repository     Size
    ========================================================================
    Installing:
    perl-Git          x86_64     1.8.2.1-1.el5        epel           49 k
    Installing for dependencies:
    git               x86_64     1.8.2.1-1.el5        epel          7.4 M
    perl-Error        noarch     1:0.17010-1.el5      epel           26 k

To verify that you have ``git`` installed::

    $ git --version
    git version 1.8.2.1

``unittest2``
-------------
``unittest2`` is a backport of the new features added to the unittest
testing framework in Python 2.7.  It is tested to run on Python 2.4 - 2.6::

    ========================================================================
    Package           Arch       Version              Repository     Size
    ========================================================================
    Installing:
    python-unittest2  noarch     0.5.1-1.el5.rf       rpmforge      183 k

``nose``
--------
``nose`` is a discovery-based unittest extension for Python::

    ========================================================================
    Package           Arch       Version              Repository     Size
    ========================================================================
    Installing:
    python-nose       noarch     0.11.3-2.el5         epel          310 k
    Installing for dependencies:
    python-setuptools noarch     0.6c5-2.el5          base          479 k

``pytz``
^^^^^^^^

``pytz`` brings the Olson tz database into Python. This library allows
accurate and cross platform timezone calculations using Python 2.3
or higher::

    ========================================================================
    Package           Arch       Version              Repository     Size
    ========================================================================
    Installing:
    pytz              noarch     2010h-1.el5          epel           35 k

pyodbc
^^^^^^

::

    ========================================================================
    Package           Arch        Version             Repository     Size
    ========================================================================
    Installing:
    pyodbc            x86_64      2.1.5-2.el5         epel           46 k

cx_Oracle
^^^^^^^^^

``cx_Oracle`` is a Python extension module that allows access to Oracle
databases and conforms to the Python database API specification.

The ``cx_Oracle`` package needs to be downloaded separately from
`cx_Oracle download page <http://cx-oracle.sourceforge.net/>`_

.. note::

    As of *release 0.14*, the ``cx_Oracle`` package release that will support the
    Toll Oracle interfaces is `CentOS 5 x86_64 RPM (Oracle 10g, Python 2.4) <http://downloads.sourceforge.net/project/cx-oracle/5.1.2/cx_Oracle-5.1.2-10g-py24-1.x86_64.rpm?r=http%3A%2F%2Fcx-oracle.sourceforge.net%2F&ts=1395266599&use_mirror=aarnet>`_

``cx_Oracle`` has a dependency on the Oracle instant client.  This can be
downloaded from the `Oracle Instant Client Downloads for Linux
<http://www.oracle.com/technetwork/topics/linuxx86-64soft-092277.html>`_

Place the downloaded executable file into ``/var/tmp`` to align with the
following commands:

#. as user root, run::

    # rpm -ivh /var/tmp/oracle-instantclient-basic-10.2.0.4-1.x86_64.rpm

#. Update dynamic library path by adding the following to the
   ``/etc/ld.so.conf`` file::

    /usr/lib/oracle/10.2.0.4/client64/lib

#. as user root, run::

    # /sbin/ldconfig

#. install cx_Oracle::

    # rpm -ivh /var/tmp/cx_Oracle-5.1.2-10g-py24-1.x86_64.rpm

``python-sphinx``
-----------------

Sphinx is a tool that makes it is used to create the documentation for the
project::

    ========================================================================
    Package           Arch        Version             Repository     Size
    ========================================================================
    Installing:
    python-sphinx     noarch      0.4.2-1.el5.1       epel          371 k

``rpm-build``
-------------

In order to build the project's RPM package, you will need to install
the ``rpm-build`` package::

    ========================================================================
    Package           Arch        Version             Repository    Size
    ========================================================================
    Installing:
    rpm-build         x86_64      4.4.2.3-34.el5      base         304 k
    Updating for dependencies:
    popt              i386       1.10.2.3-34.el5     base           77 k
    popt              x86_64     1.10.2.3-34.el5     base           79 k
    rpm               x86_64      4.4.2.3-34.el5     base          1.2 M
    rpm-libs          x86_64      4.4.2.3-34.el5     base          926 k
    rpm-python        x86_64      4.4.2.3-34.el5     base           65 k

Source Code Management
----------------------

The Toll Parcel Portal B2C Replicator package source code is maintained at
`Github <https://github.com/loum/nparcel>`_.

Cloning
^^^^^^^
To clone the project into the directory ``nparcel`` on your local
filesystem::

    $ git clone https://github.com/loum/nparcel.git
    Initialized empty Git repository in /home/lupco/dev/nparcel/.git/
    remote: Counting objects: 4, done.
    remote: Compressing objects: 100% (3/3), done.
    remote: Total 4 (delta 0), reused 0 (delta 0)
    Unpacking objects: 100% (4/4), done.

Pushing to the repository
^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::

    the ``loum`` repository is currently set to **private**.
    Ask `the maintainer <loumar@tollgroup.com>`_ for write access or simply
    create your own repository.

Standard ``git`` here::

    $ git push origin <branch>


Packaging
---------

Software releases are managed by the standard RedHat RPM packaging process
using the :mod:`distutils` module.

Package Build
^^^^^^^^^^^^^

A package can be built from within the top level of your local version of
the source code repository.  For example, if you cloned the project into the
directory ``nparcel``, then execute these commands::

    $ cd nparcel
    $ make build

This will create the package under the ``dist`` directory::

    $ ls -1 dist
    python-nparcel-0.31-1.noarch.rpm
    python-nparcel-0.31-1.src.rpm
    python-nparcel-0.31.tar.gz

The ``python-nparcel-0.31-1.noarch.rpm`` package is given to your friendly
UNIX Admin who will be able to install the software.

.. note::

    The package versioning (for example, ``0.31`` as above) can be altered
    within the ``nparcel/setup.py`` file under the top level of the project
    repository.

Package Installation
^^^^^^^^^^^^^^^^^^^^

If you have ``root`` privilleged access to your RedHat-variant box you can
install the package yourself.

.. note::

    RPM package installation must be run as the ``root`` user

If this is an upgrade, remove the old version of the package.  The latest
package version can be obtained with::

    $ rpm -qi python-nparcel
    Name        : python-nparcel               Relocations: /usr 
    Version     : 0.31                              Vendor: Lou Markovski <lou.markovski@tollgroup.com>
    Release     : 1                             Build Date: Tue 04 Mar 2014 15:15:23 EST
    Install Date: Tue 04 Mar 2014 15:15:33 EST      Build Host: titanium.toll.com.au
    Group       : Development/Libraries         Source RPM: python-nparcel-0.31-1.src.rpm
    Size        : 3635424                          License: UNKNOWN
    Signature   : (none)
    URL         : https://nparcel.tollgroup.com
    Summary     : Nparcel B2C Replicator
    Description :
    UNKNOWN

To uninstall an old package::

    # rpm -e python-nparcel

To install the new package (provided the new package has been placed in
``/var/tmp/python-nparcel-0.31-1.noarch.rpm``)::

    # rpm -qi /var/tmp/python-nparcel-0.31-1.noarch.rpm

FAQs
----
**Q.** The Toll proxy is making my life miserable :-(

**A.** Yes, this is a common symptom within Toll.  Simply set your shell
as follows to make your life that much easier ... ::

    $ export https_proxy="http://<username>:<password>@auproxy-farm.toll.com.au:8080"

**Q.** I tried to commit and received this terribly confusing message::

    (gnome-ssh-askpass:12653): Gtk-WARNING **: cannot open display: 

**A.** Don't panic.  This occurs because the ``SSH_ASKPASS`` environment
variable is set.  This tries to open a ``gtk`` window to accept a hidden
password.  It will fail unless you have set up your environmen to handle X.
To bypass, change ``SSH_ASKPASS`` to something else.  This can be done in
``~/.bash_aliases``::

    alias git="SSH_ASKPASS='' git"
