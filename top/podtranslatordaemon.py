__all__ = [
    "PodTranslatorDaemon",
]
import signal
import time
import os
import datetime

import top
from top.utils.log import log
from top.utils.files import (move_file,
                             copy_file,
                             remove_files)
from top.utils.setter import (set_scalar,
                              set_list)


class PodTranslatorDaemon(top.DaemonService):
    """Daemoniser facility for the :class:`top.PodTranslator` class.

    .. attribute:: file_formats

        list of :mod:`re` format strings to match filter files against

    .. attribute:: out_dir

        outbound directory to place transposed files

    .. attribute:: archive_dir

        base directory where working files are archived to

    """
    _file_formats = []
    _out_dir = None
    _archive_dir = None

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config=None):
        top.DaemonService.__init__(self,
                                   pidfile=pidfile,
                                   file=file,
                                   dry=dry,
                                   batch=batch,
                                   config=config)

        if self.config is not None:
            self.set_loop(self.config.pod_translator_loop)
            self.set_in_dirs(self.config.pod_dirs)
            self.set_out_dir(self.config.out_dir)
            self.set_archive_dir(os.path.join(self.config.archive_dir,
                                              'podtranslated'))
            self.set_file_formats(self.config.file_formats)

    @property
    def out_dir(self):
        return  self._out_dir

    @set_scalar
    def set_out_dir(self, value):
        pass

    @property
    def archive_dir(self):
        return  self._archive_dir

    @set_scalar
    def set_archive_dir(self, value):
        pass

    @property
    def file_formats(self):
        return self._file_formats

    @set_list
    def set_file_formats(self, values=None):
        pass

    def _start(self, event):
        """Override the :method:`top.utils.Daemon._start` method.

        Will perform a single iteration if the :attr:`file` attribute has
        a list of filenames to process.  Similarly, dry and batch modes
        only cycle through a single iteration.

        **Args:**
            *event* (:mod:`threading.Event`): Internal semaphore that
            can be set via the :mod:`signal.signal.SIGTERM` signal event
            to perform a function within the running proess.

        """
        signal.signal(signal.SIGTERM, self._exit_handler)

        pt = top.PodTranslator()

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

                if batch_status:
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
                else:
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
            if os.path.exists(key_file):
                status = move_file(key_file,
                                os.path.join(target_dir,
                                                os.path.basename(key_file)),
                                dry=dry)

        return status
