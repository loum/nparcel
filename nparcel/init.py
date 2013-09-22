__all__ = [
    "Ftp",
]
import os
import shutil
import datetime
import ConfigParser

import nparcel
from nparcel.utils.log import log


class Init(object):
    """Nparcel initialiser.

    .. attribute:: base_dir

        The target directory to copy files.  Default is
        ``~<user_home>/.nparceld``

    .. attribute:: unconditional_files

        Files that are unconditionally copied.

    .. attribute:: unconditional_dirs

        Directories whose contents are unconditionally copied.

    .. attribute:: conditional_files

        Files that are conditionally copied (will not clobber existing
        file).

    .. attribute:: conditional_dirs

        Directories whose contents are conditionally copied (will not
        clobber existing files).

    """

    def __init__(self,
                 config_file=None,
                 base_dir=os.path.join(os.path.expanduser('~'),
                                       '.nparceld')):
        """Nparcel Initialiser initialiser.
        """
        path = os.path.join(self.path, 'conf', 'init.conf')
        if config_file is not None:
            path = config_file
        log.debug('Preparing initialisation config file: "%s"' % path)
        self.conf = nparcel.Config(config_file=path)
        self._base_dir = base_dir

        self._unconditional_files = []
        self._unconditional_dirs = []
        self._conditional_files = []
        self._conditional_dirs = []

    @property
    def base_dir(self):
        return self._base_dir

    def set_base_dir(self, value):
        self._base_dir = value

    @property
    def path(self):
        return os.path.dirname(os.path.realpath(__file__))

    @property
    def unconditional_files(self):
        return self._unconditional_files

    def set_unconditional_files(self, values):
        del self._unconditional_files[:]

        if values and values is not None:
            self._unconditional_files.extend(values)
        else:
            self._unconditional_files = []

    @property
    def unconditional_dirs(self):
        return self._unconditional_dirs

    def set_unconditional_dirs(self, values):
        del self._unconditional_dirs[:]

        if values and values is not None:
            self._unconditional_dirs.extend(values)
        else:
            self._unconditional_dirs = []

    @property
    def conditional_files(self):
        return self._conditional_files

    def set_conditional_files(self, values):
        del self._conditional_files[:]

        if values and values is not None:
            self._conditional_files.extend(values)
        else:
            self._conditional_files = []

    @property
    def conditional_dirs(self):
        return self._conditional_dirs

    def set_conditional_dirs(self, values):
        del self._conditional_dirs[:]

        if values and values is not None:
            self._conditional_dirs.extend(values)
        else:
            self._conditional_dirs = []

    @property
    def conditionals(self):
        conditionals = self.conditional_files

        for dir in self.conditional_dirs:
            files = [os.path.join(dir, x) for x in os.listdir(dir)]
            if len(files):
                conditionals.extend(files)

        return conditionals

    @property
    def unconditionals(self):
        unconditionals = list(self.unconditional_files)

        for dir in self.unconditional_dirs:
            files = [os.path.join(dir, x) for x in os.listdir(dir)]
            if len(files):
                unconditionals.extend(files)

        return unconditionals

    def parse_config(self):
        """Read config items from the initialisation configuration file.

        """
        msg = 'Init unconditional files'
        try:
            files = self.conf.get('unconditional', 'files')
            if files:
                self.set_unconditional_files(files.split(','))
            log.debug('%s: "%s"' % (msg, self.unconditional_files))
        except ConfigParser.NoOptionError, err:
            log.warn('%s: "%s"' % (msg, err))

        msg = 'Init unconditional directories'
        try:
            dirs = self.conf.get('unconditional', 'dirs')
            if dirs:
                self.set_unconditional_dirs(dirs.split(','))
            log.debug('%s: "%s"' % (msg, self.unconditional_dirs))
        except ConfigParser.NoOptionError, err:
            log.warn('%s: "%s"' % (msg, err))

        msg = 'Init conditional files'
        try:
            cond_files = self.conf.get('conditional', 'files')
            if cond_files:
                self.set_conditional_files(files.split(','))
            log.debug('%s: "%s"' % (msg, self.conditional_files))
        except ConfigParser.NoOptionError, err:
            log.warn('%s: "%s"' % (msg, err))

        msg = 'Init conditional directories'
        try:
            cond_dirs = self.conf.get('conditional', 'dirs')
            if cond_dirs:
                self.set_conditional_dirs(cond_dirs.split(','))
            log.debug('%s: "%s"' % (msg, self.conditional_dirs))
        except ConfigParser.NoOptionError, err:
            log.warn('%s: "%s"' % (msg, err))

    def copy_file(self, source_file, dir=None, conditional=True, dry=False):
        """Attempts to copy *source_file* to the :attr:`base_dir`

        **Args:**
            *source_file*: name of the file to copy.

        **Kwargs:**
            *dir*: directory (off :attr:`base_dir`) to copy *source_file*
            to.

            *conditional*: flag to copy *source_file* conditionally (only if
            file does not exit) of unconditionally (clobber).  Default is
            conditionally.

            *dry*: only report, do not actual execute

        **Returns:**
            boolean ``True`` if copy occurred without error

            boolean ``False`` if copy did not occur

        """
        status = False

        target_dir = self.base_dir
        if dir is not None:
            target_dir = os.path.join(self.base_dir, dir)

        copy = True
        if not os.path.exists(target_dir):
            log.debug('Creating directory: "%s"' % target_dir)
            try:
                if not dry:
                    os.makedirs(target_dir)
            except OSError, err:
                copy = False
                log.error('Unable to create target directory "%s": %s' %
                          (target_dir, err))

        target_file = os.path.join(target_dir,
                                   os.path.basename(source_file))
        backup = False
        if copy and os.path.exists(target_file):
            if conditional:
                log.warn('Target file "%s" exists' % target_file)
                copy = False
            else:
                backup = True

        if backup:
            ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            backup_file = "%s.%s" % (target_file, ts)
            log.info('Backup file "%s"' % target_file)
            if not dry:
                try:
                    shutil.copyfile(target_file, backup_file)
                except IOError, err:
                    log.error('Copy error: "%s"' % err)
                    copy = False

        if copy:
            log.info('Copying "%s" to "%s" ' % (source_file, target_file))
            if not dry:
                try:
                    shutil.copyfile(source_file, target_file)
                    status = True
                except IOError, err:
                    log.error('Copy error: "%s"' % err)

        return status
