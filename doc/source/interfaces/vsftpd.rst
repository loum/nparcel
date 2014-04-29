.. Toll Outlet Portal Middleware Inbound FTP (vsftpd)

.. toctree::
    :maxdepth: 2

Inbound FTP
===========
Each Business Unit must capture failed parcel delivery information into
the standard 1250 EDI file.  These files must be periodically
be transferred to the Toll Outlet Portal middleware via FTP.

The Toll Outlet Portal middleware presents a inbound FTP drop box for
each Business Unit.

.. _ftp_drop_box:

Prepare an Inbound Drop-box
---------------------------
All Business Units have their own drop box details which branches off the
generic ``/var/ftp/pub/top`` directory structure.  For example, in the
case of Business Unit **Priority**, the inbound FTP directory would be
``/var/ftp/pub/top/priority/in``.

To create the directory, as the user ``npprod`` run the command::

    $ mkdir -p /var/ftp/pub/top/priority/in

Create the Business Unit FTP user
---------------------------------
As each Buiness Unit comes online, we need to give them credentials to be
able to connect to their own T1250* drop-box.  The Business Unit will
connect to the Toll Outlet Portal's FTP server with these credentials.

First add the new Business Unit username and password to the
``/opt/virtual-users.txt`` file::

    $ sudo sudoedit /opt/virtual-users.txt

.. note::

    the ``virtual-users.txt`` file accepts the username and password on
    separate lines.

For example, if Priority's username is ``priority`` and password is
``<passwd>``, the appropriate entires would be::

    priority
    <passwd>

Similarly, add the username to the ``/etc/vsftpd/vsftpd.userlist`` file::

    $ sudo sudoedit /etc/vsftpd/vsftpd.userlist

Add the new user to the FTP Server's users database::

    $ sudo /usr/bin/db_load -T -t hash -f /opt/virtual-users.txt /etc/vsftpd/virtual-users.db

Finally, restart the FTP server::

    $ sudo /etc/init.d/vsftpd stop
    $ sudo /etc/init.d/vsftpd start
