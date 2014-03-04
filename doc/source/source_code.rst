.. B2C Middleware Source Code Repository and Packaging

B2C Middleware Source Code Repository and Packaging
===================================================

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

    $ export https_proxy="http://<username>:<password>@itproxy-farm.toll.com.au:8080"

**Q.** I tried to commit and received this terribly confusing message::

    (gnome-ssh-askpass:12653): Gtk-WARNING **: cannot open display: 

**A.** Don't panic.  This occurs because the ``SSH_ASKPASS`` environment
variable is set.  This tries to open a ``gtk`` window to accept a hidden
password.  It will fail unless you have set up your environmen to handle X.
To bypass, change ``SSH_ASKPASS`` to something else.  This can be done in
``~/.bash_aliases``::

    alias git="SSH_ASKPASS='' git"
