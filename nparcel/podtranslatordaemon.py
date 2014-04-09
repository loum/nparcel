__all__ = [
    "PodTranslatorDaemon",
]
import signal
import time
import os
import datetime

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import (move_file,
                                 copy_file,
                                 remove_files)


class PodTranslatorDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.PodTranslator` class.

    .. attribute:: file_formats

        list of :mod:`re` format strings to match filter files against

    .. attribute:: out_dir

        outbound directory to place transposed files

    .. attribute:: archive_dir

        base directory where working files are archived to

    """
    _config = None
    _file_formats = []
    _out_dir = None
    _archive_dir = None

    @property
    def out_dir(self):
        return  self._out_dir

    def set_out_dir(self, value=None):
        self._out_dir = value
        log.debug('%s out_dir set to: "%s"' %
                  (self.facility, str(self.out_dir)))

    @property
    def archive_dir(self):
        return  self._archive_dir

    def set_archive_dir(self, value=None):
        self._archive_dir = value
        log.debug('%s archive_dir set to: "%s"' %
                  (self.facility, str(self.archive_dir)))

    @property
    def file_formats(self):
        return self._file_formats

    def set_file_formats(self, values=None):
        del self._file_formats[:]
        self._file_formats = []

        if values is not None:
            self._file_formats.extend(values)
        log.debug('%s file_formats set to: "%s"' %
                  (self.facility, self.file_formats))

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config=None):
        nparcel.DaemonService.__init__(self,
                                       pidfile=pidfile,
                                       file=file,
                                       dry=dry,
                                       batch=batch)

        if config is not None:
            self.config = nparcel.PodB2CConfig(file=config)
            self.config.parse_config()

        try:
            self.set_loop(self.config.pod_translator_loop)
        except AttributeError, err:
            log.debug('%s loop not in config: %s. Using %d (sec)' %
                      (self.facility, err, self.loop))

        try:
            if len(self.config.pod_dirs):
                self.set_in_dirs(self.config.pod_dirs)
            else:
                raise
        except AttributeError, err:
            log.debug('%s inbound dir not in config: %s. Using "%s"' %
                      (self.facility, err, self.in_dirs))

        try:
            self.set_out_dir(self.config.out_dir)
        except AttributeError, err:
            log.debug('%s out dir not in config: %s. Using "%s"' %
                      (self.facility, err, self.out_dir))

        try:
            self.set_archive_dir(os.path.join(self.config.archive_dir,
                                              'podtranslated'))
        except AttributeError, err:
            log.debug('%s out dir not in config: %s. Using "%s"' %
                      (self.facility, err, self.out_dir))

        try:
            if self.config.file_formats is not None:
                self.set_file_formats(self.config.file_formats)
        except AttributeError, err:
            log.debug('%s file_formats not in config: %s. Using %s' %
                      (self.facility, err, self.file_formats))

    def _start(self, event):
        """Override the :method:`nparcel.utils.Daemon._start` method.

        Will perform a single iteration if the :attr:`file` attribute has
        a list of filenames to process.  Similarly, dry and batch modes
        only cycle through a single iteration.

        **Args:**
            *event* (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        pt = nparcel.PodTranslator()

        while not event.isSet():
            files = []
            if self.file is not None:
                files.append(self.file)
                event.set()
            else:
                files.extend(self.get_files(formats=self.file_formats))

            # Start processing files.
            self.reporter.reset(identifier=str())
            for file in files:
                keys = pt.process(file=file, dry=self.dry)

                dir = os.path.dirname(file)
                batch_status = True
                for key in keys:
                    status = self.move_signature_files(key,
                                                       dir,
                                                       self.out_dir,
                                                       dry=self.dry)

                    if not status:
                        log.error('Token "%s" move failed' % key)
                        batch_status = False

                if batch_status and not self.dry:
                    # If all OK, move the report file (atomically).
                    copy_file('%s.xlated' % file,
                              os.path.join(self.out_dir,
                                           os.path.basename(file)))
                    remove_files('%s.xlated' % file)

                    # ... and archive.
                    dmy = datetime.datetime.now().strftime('%Y%m%d')
                    archive_dir = os.path.join(self.archive_dir, dmy)
                    log.info('Archiving "%s"' % file)
                    move_file(file, os.path.join(archive_dir,
                                                 os.path.basename(file)))
                elif not batch_status:
                    log.error('POD translation failed for: "%s"' % file)
                    # ... and move aside.
                    move_file(file, '%s.err' % file, dry=self.dry)

                self.reporter(batch_status)

            if len(files):
                log.info(self.reporter.report())

            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.loop)

    def move_signature_files(self,
                             token,
                             source_dir,
                             target_dir,
                             dry=False):
        """Move the signature files based on *token* from *source_dir*
        to *target_dir*.  The search will assume a ``.ps`` and ``.png``
        file extension.

        **Args:**
            *token*: string to use in the signature filename search

            *source_dir*: directory to search for signature files

            *target_dir*: directory to place signature files into (if found)

            *dry*: only report, don't run

        **Returns:**
            boolean ``True`` if move was successful

            boolean ``False`` if move failed (or was a dry run)

        """
        status = False

        # Move to the outbound directory.
        for ext in ['ps', 'png']:
            key_file = os.path.join(source_dir, '%s.%s' % (token, ext))
            status = move_file(key_file,
                               os.path.join(target_dir,
                                            os.path.basename(key_file)),
                               dry=dry)

        return status
