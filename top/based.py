__all__ = [
    "BaseD",
]
import os
from optparse import OptionParser

from top.utils.setter import (set_scalar,
                              set_list)
from top.utils.log import (log,
                           set_console,
                           set_log_level)


class BaseD(object):
    """Base daemoniser.

    .. attribute:: config

        location of the daemon configuration file

    .. attribute:: usage

        program usage

    .. attribute:: parser

        handle to a :class:`optparse.OptionParser` object

    .. attribute:: options

        object containing values for all options

    .. attribute:: args

        list of positional arguments leftover after parsing options

    .. attribute:: command

        the command to execute

    .. attribute:: dry

        only report, do not execute flag (single iteration)

    .. attribute:: batch

        single iteration execution flag

    .. attribute:: pidfile

        name of the PID file

    .. attribute:: supported_commands

        list of supported command names

    """
    _config = os.path.join(os.path.expanduser('~'), '.top', 'top.conf')
    _usage = 'usage: %prog [options] start|stop|status'
    _parser = OptionParser(usage=_usage)
    _options = None
    _args = []
    _dry = False
    _command = None
    _batch = False
    _pidfile = None
    _script_name = None
    _supported_commands = ['start', 'stop', 'status']

    @property
    def config(self):
        return self._config

    @set_scalar
    def set_config(self, value):
        pass

    @property
    def usage(self):
        return self._usage

    @set_scalar
    def set_usage(self, value):
        pass

    @property
    def parser(self):
        return self._parser

    @property
    def options(self):
        return self._options

    @set_scalar
    def set_options(self, value):
        pass

    @property
    def args(self):
        return self._args

    @set_list
    def set_args(self, values=None):
        pass

    @property
    def command(self):
        return self._command

    @set_scalar
    def set_command(self, value):
        pass

    @property
    def dry(self):
        return self._dry

    @set_scalar
    def set_dry(self, value):
        pass

    @property
    def batch(self):
        return self._batch

    @set_scalar
    def set_batch(self, value):
        pass

    @property
    def pidfile(self):
        if self._pidfile is None and self._script_name is not None:
            self._pidfile = os.path.join(os.path.expanduser('~'),
                                         '.top',
                                         'pids',
                                         '%s.pid' % self._script_name)

        return self._pidfile

    @set_scalar
    def set_pidfile(self, value):
        pass

    @property
    def script_name(self):
        return self._script_name

    @set_scalar
    def set_script_name(self, value):
        pass

    @property
    def supported_commands(self):
        return self._supported_commands

    @set_list
    def set_supported_commands(self, values=None):
        pass

    def __init__(self, config=None):
        """BaseD initialisation.
        """
        if config is not None:
            self._config = config

        self._parser.add_option("-v", "--verbose",
                                dest="verbose",
                                action="count",
                                default=0,
                                help="raise logging verbosity")
        self._parser.add_option('-d', '--dry',
                                dest='dry',
                                action='store_true',
                                help='dry run - report only, do not execute')
        self._parser.add_option('-b', '--batch',
                                dest='batch',
                                action='store_true',
                                help='single pass batch mode')
        self._parser.add_option('-c', '--config',
                                dest='config',
                                default=self._config,
                                help=('override default config "%s"' %
                                      self._config))

    def check_args(self, script_name, command=None):
        """Verify that the daemon arguments are as expected.

        Sets the controller command to (for example stop, start or status)
        unless :attr:`command` is predefined.

        Attempts to make a sane assesment of options against the given
        :attr:`command`.

        **Args**:
            *script_name*: name of the executing script

        **Kwargs**:
            *command*: name of the executing script

        **Raises**:
            ``SystemExit`` (program exit) if one argument is not provided
            on the command line (unless the :attr:`command` is predefined.

        """
        (options, args) = self.parser.parse_args()

        if options.dry is not None:
            set_console()

        cmd = command
        if command is None:
            if len(args) != 1:
                self.parser.error("incorrect number of arguments")

            cmd = (args.pop(0))

            if (cmd not in self.supported_commands):
                self.parser.error('command "%s" not supported' % cmd)

            if (cmd != 'start' and
                (options.dry or options.batch)):
                self.parser.error('invalid option(s) with command "%s"' %
                                  cmd)

        if cmd == 'status':
            set_console()

        if options.verbose == 0:
            set_log_level('INFO')
        else:
            log.debug('Logging verbosity set to "DEBUG" level')

        self.set_command(cmd)
        self.set_script_name(script_name)
        self.set_options(options)
        self.set_args(args)

        if self.command == 'start':
            self.set_dry(self.options.dry is not None)
            self.set_batch(self.options.batch is not None)

    def launch_command(self, obj, script_name):
        """Run :attr:`command` based on *obj* context.

        Supported command are start, stop and status.

        **Args:**
            *obj*: the :class:`top.Daemon` based object instance
            to launch the command against.

            *script_name*: the calling script's name

        """
        if self.command == 'start':
            msg = 'Starting %s' % script_name
            if self.dry:
                msg = '%s inline' % msg
            else:
                msg = '%s as daemon' % msg
            if self.batch:
                msg = '%s (batch mode)' % msg

            print('%s ...' % msg)
            obj.set_inline(self.dry)
            if not obj.start():
                print('Start aborted')
        elif self.command == 'stop':
            print('Stopping %s ...' % script_name)
            if obj.stop():
                print('OK')
            else:
                print('Stop aborted')
        elif self.command == 'status':
            if obj.status():
                print('%s is running with PID %d' % (script_name, obj.pid))
            else:
                print('%s is idle' % script_name)
        else:
            print('Do not know command "%s"' % self.command)
