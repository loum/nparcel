.. Nparcel B2C Source Code Repository

Nparcel B2C Source Code Repository
==================================

The Nparcel B2C Replicator package source code is maintained at
`Github <https://github.com/loum/nparcel>`_.

Cloning
-------
To clone the project into the directory ``nparcel`` on your local
filesystem::

    $ git clone https://github.com/loum/nparcel.git
    Initialized empty Git repository in /home/lupco/dev/nparcel/.git/
    remote: Counting objects: 4, done.
    remote: Compressing objects: 100% (3/3), done.
    remote: Total 4 (delta 0), reused 0 (delta 0)
    Unpacking objects: 100% (4/4), done.

Pushing to the repository
-------------------------
.. note::

    the ``loum`` repository is currently set to **private**.
    Ask `the maintainer <loumar@tollgroup.com>`_ for write access or simply
    create your own repository.

Standard ``git`` here::

    $ git push origin <branch>

FAQs
^^^^
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
