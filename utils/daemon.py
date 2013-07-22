"""The :mod:`nparcel.utils.daemon` module provides your server with start
and stop functionality.  Furthermore, it supports process daemonisation so
that the server could be run as a self-contained Linux service.

.. note::

    Bulk of this code was taken from
    http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
    with some re-work.

"""
__all__ = [
    "Daemon",
    "DaemonError",
]

import sys
import logging
import os
import resource
import atexit
import signal
import time
import threading

from nparcel.utils.log import log, autolog

MAXFD = 1024


class Daemon(object):
    """A generic daemon class.

    :class:`nparcel.utils.Daemon` will prepare the daemon environment for
    you but expects that you give it an entry point (:meth:`_start`) to
    the functional component of your process.

    The following example shows a trivial class that defines a
    :meth:`_start`
    method ...

    >>> import nparcel.utils
    >>> import time
    >>> class DummyDaemon(nparcel.utils.Daemon):
    ...     def _start(self, event):
    ...         while True:
    ...             time.sleep(5)
    ...
    >>> d = DummyDaemon(pidfile='/var/tmp/pidfile')
    >>> d.start()
    True
    ...

    And later, to stop:

    >>> d.stop()
    True
    ...

    The :meth:`start` method manages the daemonisation of the environment
    and makes the actual call to your own instance of the :meth:`_start`
    method.

    .. note:;

        All public attribute access is implemented in a Pythonic property
        decorator style.

    .. attribute:: exit_event (:class:`threading.Event`)

        Internal semaphore that when set, signals that the server process
        is to be terminated.
    """

    def __init__(self,
                 pidfile,
                 term_parent=True):
        """Daemon class initialiser.

        :class:`Daemon` is built on top the the :mod:`abc` Abstract Base
        Class module and is defined as *abstract*.  It is not intended to
        be instantiated directly.  Instead, it forces generalisations
        to define their own :meth:`_start` method.  :meth:`_start`
        will be called after the process has been daemonised by
        :meth:`start` or :meth:`restart`.

        :class:`Daemon` expects the caller to define a *pidfile*.  Otherwise
        the *pidfile* will default to ``None`` and all deamonisation will
        be suppressed.  Any attempts to call methods without a *pidfile*
        will raise an exception.

        **Args:**
            pidfile (str): Path to the PID file.

        **Kwargs:**
            term_parent (boolean): Attempt to terminate the parent to
            enforce true separation between parent and child processes.
            Useful when running under test scenarios as :mod:`unittest2`
            barfs if you try to kill it.  Defaults to ``True``.

        **Raises:**
            ``IOError`` if *pidfile* is not writable.

        """
        self._pidfile = pidfile
        self._term_parent = term_parent

        self._exit_event = threading.Event()

        self.pid = None
        self.pidfs = None

        # Only validate settings if a pidfile was specified.
        if self.pidfile is not None:
            self._validate()

    @property
    def pidfile(self):
        return self._pidfile

    def set_pidfile(self, value):
        self._pidfile = value

    @property
    def term_parent(self):
        return self._term_parent

    @property
    def exit_event(self):
        return self._exit_event

    def set_exit_event(self, value):
        self._exit_event = value

    def _start(self):
        """Define this method within your class generalisation with logic
        that invokes your process to benefit from the daemonisation
        facility.  In fact, the method is abstract to force you to do just
        that.  The method should contain the logic that invokes your
        process.

        Consider this method to be private in the sense that it should not
        be invoked directly.  Instead, allow the context of the process
        invocation (either as a deamon or inline), to prepare the
        environment for you.  From within your class, all you need to do
        is call the :meth:`nparcel.utils.Daemon.start` method.

        **Kwargs:**
            event (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        pass

    def _validate(self):
        """Validator method called during object initialisation.

        ..note::

            When starting a new process, the PID file will be relative
            to '/' once the process is forked.

        **Raises:**
            :mod:`nparcel.utils.daemon.DaemonError` if *pidfile* contains
            invalid content.

        """
        if not os.path.isabs(self.pidfile):
            autolog('PID file "%s" is relative -- make absolute' %
                    self.pidfile)
            self.pidfile = os.path.join(os.sep, self.pidfile)
            autolog('PID file now "%s"' % self.pidfile)

        # Check if the PID file exists.
        if os.path.exists(self.pidfile):
            # PID file exists, so the process may be active.
            # Set the current process PID.
            autolog('PID file "%s" exists' % self.pidfile)
            try:
                self.pid = int(file(self.pidfile, 'r').read().strip())
                autolog('Stored PID is: %d' % self.pid)
            except ValueError, err:
                raise DaemonError('Error reading PID file: %s' % err)

    def start(self):
        """Wrapper around the server start process.

        Invokes the server in one of two ways:

        * As a daemon
        * Inline using the :mod:`threading.Event` module

        Typically, the daemon instance will be used in a production
        environment and the inline instance for testing or via the
        Python interpreter.

        .. note::

            :mod:`unittest` barfs if the method under test exits :-(

        The distinction between daemon or inline mode is made during object
        initialisation.  If you specify a *pidfile* then it will assume
        you want to run as a daemon.

        **Returns:**
            boolean::

                ``True`` -- success
                ``False`` -- failure

        """
        start_status = False

        start_status = self._start_daemon()

        return start_status

    def _start_daemon(self):
        """Start the daemon process.

        ..note::

            Daemon will only start if PID file exists (not ``None``).

        The :meth:`start` method checks for an existing PID before
        preparing the daemon environment.  Finally, it will initiate
        the daemon process run sequence.

        **Returns:**
            boolean::

                ``True`` -- success
                ``False`` -- failure

        **Raises:**
            :mod:`nparcel.utils.daemon.DaemonError`, if:

            * PID file has not been defined
            * PID file is not writable

        """
        start_status = False

        # If we have got this far, check that we have a valid PID file.
        if self.pidfile is None:
            raise DaemonError('PID file has not been defined')

        autolog('checking daemon status with PID: %s' % self.pid)
        if self.pid is not None:
            msg = ('PID file "%s" exists.  Daemon may be running?\n' %
                   self.pidfile)
            log.error(msg)
        else:
            # Check if PID file is writable to save hassles later on.
            autolog('No PID file -- creating handle')
            try:
                autolog('starting daemon')
                self.daemonize()
                self._start(self.exit_event)
                start_status = True
            except IOError, err:
                err_msg = 'Cannot write to PID file: IOError "%s"' % err
                raise DaemonError(err_msg)

        return start_status

    def daemonize(self):
        """Prepare the daemon environment.

        Does the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177).

        The second child PID is written out to the PID file.  This acts
        as a persistent state check, where no file implies that the
        daemon process is idle.

        The daemon process environment acts as a container for your process
        logic.  As such, once the daemon process ends it will remove its
        associated PID file automatically.

        """
        autolog('attempting first fork')
        try:
            pid = os.fork()

            # Exit first parent.
            if pid > 0:
                if self.term_parent:
                    sys.exit(0)
                else:
                    return
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno,
                                                            e.strerror))
            sys.exit(1)

        # Decouple from parent environment.
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Do second fork.
        try:
            pid = os.fork()

            # Exit from second parent.
            if pid > 0:
                if self.term_parent:
                    sys.exit(0)
                else:
                    return
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno,
                                                            e.strerror))
            sys.exit(1)

        # Close all file descriptors except from non-console logging
        # handlers.
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if (maxfd == resource.RLIM_INFINITY):
            maxfd = MAXFD

        filenos = []
        for handler in logging.root.handlers:
            if (hasattr(handler, 'stream') and
                hasattr(handler.stream, 'fileno') and
                handler.stream.fileno() > 2):
                filenos.append(handler.stream.fileno())
            for fd in range(0, maxfd):
                try:
                    if fd not in filenos:
                        os.close(fd)
                except OSError:
                    pass

        # Redirect stdin, stdout, stderr to null
        os.open(os.devnull, os.O_RDWR)
        os.dup2(0, 1)
        os.dup2(0, 2)

        # Write out to pidfile.
        child_pid = str(os.getpid())
        autolog('PID of child process: %s' % child_pid)
        file(self.pidfile, 'w+').write("%s\n" % child_pid)

        # Remove the PID file when the process terminates.
        atexit.register(self._delpid)

    def stop(self):
        """Stop the daemon.

        Will run a series of checks around the existence of a PID file
        before attempting to terminate the daemon.

        **Returns:**
            boolean::

                ``True`` -- success
                ``False`` -- failure

        """
        stop_status = False

        if self.pid:
            # OK to terminate.
            autolog('stopping daemon process with PID: %s' % self.pid)

            try:
                os.kill(int(self.pid), signal.SIGTERM)
            except OSError, err:
                log.warn('err: %s' % str(err))
                log.warn('PID "%s" does not exist' % self.pid)
                if err.errno == 3:
                    # For a daemon process, remove the PID file.
                    if self.pidfile is not None:
                        log.warn('Removing PID file "%s"' % self.pidfile)
                        if os.path.exists(self.pidfile):
                            os.remove(self.pidfile)
            else:
                stop_status = True
                self.pid = None
        elif self.pid is None:
            # PID or PID file does not exist.
            log.warn('Stopping process but unable to find PID')
        else:
            # Should not happen, but ...
            log.warn('PID file exists with invalid value: "%s"' %
                     str(self.pid))

        return stop_status

    def restart(self):
        """Restart the daemon

        No real magic here -- simply calls the :meth:`stop` and
        :meth:`start` method sequence (in that order)

        .. note::

            TODO - Need better tests around this process.

        """
        log_msg = '%s daemon --' % type(self).__name__
        log.info('%s attempting restart ...' % log_msg)
        log.info('%s stopping ...' % log_msg)
        self.stop()

        # Allow some time between restarts.
        time.sleep(2)

        log.info('%s attempting restart ...' % log_msg)
        self.start()

    def _delpid(self):
        """Simple wrapper method around file deletion.
        """
        autolog('Removing PID file at "%s"' % self.pidfile)
        os.remove(self.pidfile)

    def status(self):
        """
        **Returns:**
            boolean::

                ``True`` -- PID is active
                ``False`` -- PID is inactive

        """
        process_status = False

        if self.pid is not None:
            try:
                os.kill(int(self.pid), 0)
                process_status = True
            except OSError:
                pass

        return process_status


class DaemonError(Exception):
    """Standard exception for a Daemon error.

    Very simplistic at the moment in that it only caters for situations
    where functionality is requested without a valid PID file specified.

    .. attribute:: msg

        An explanation of the error.
    """

    def __init__(self, value):
        self.msg = value

    def __str__(self):
        return repr(self.msg)
