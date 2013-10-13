__all__ = [
    "MapperDaemon",
]
import signal
import time
import re
import os

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import get_directory_files


class MapperDaemon(nparcel.DaemonService):
    """Daemoniser facility for the :class:`nparcel.Loader` class.
    """

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False,
                 batch=False,
                 config='nparcel.conf'):
        super(MapperDaemon, self).__init__(pidfile=pidfile,
                                           file=file,
                                           dry=dry,
                                           batch=batch)

        self.config = nparcel.B2CConfig(file=config)
        self.config.parse_config()

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

        files = []
        if self.file is not None:
            files.append(self.file)
            event.set()
        else:
            files.extend(self.get_files())

        # Start processing files.
        for file in files:
            log.info('Processing file: "%s" ...' % file)

        while not event.isSet():
            if not event.isSet():
                if self.dry:
                    log.info('Dry run iteration complete -- aborting')
                    event.set()
                elif self.batch:
                    log.info('Batch run iteration complete -- aborting')
                    event.set()
                else:
                    time.sleep(self.config.loader_loop)

    def get_files(self, dir=None):
        """Identifies GIS-special WebMethod files that are to be processed.

        **Args:**
            *dir*: directory to search

        **Returns:**
            date sorted list of WebMethods files to process

        """
        files_to_process = []

        dirs_to_check = []
        if dir is not None:
            dirs_to_check.append(dir)
        else:
            dirs_to_check = self.config.pe_in_dirs

        log.debug('file format: %s' % self.config.pe_in_file_format)
        r = re.compile(self.config.pe_in_file_format)
        for dir_to_check in dirs_to_check:
            log.info('Looking for files at: %s ...' % dir_to_check)
            for file in get_directory_files(dir_to_check):
                log.debug('Checking format of file: %s' % file)
                m = r.match(os.path.basename(file))
                if m:
                    log.info('Found file: %s' % file)

                    # Check that it's not in the archive already.
                    archive_path = self.get_customer_archive(file)
                    if (archive_path is not None and
                        os.path.exists(archive_path)):
                        log.error('File %s is already archived -- skipped' %
                                  file)
                    else:
                        files_to_process.append(file)

        files_to_process.sort()
        log.debug('Files set to be processed: "%s"' % str(files_to_process))

        return files_to_process

    def get_customer_archive(self, file):
        """Returns the archive target path based on GIS T1250 filename
        *file*.  For example, if the source file is
        ``<ftp_base>/nparcel/in/T1250_TOLI_20131011115618.dat`` then the
        archive target would be similar to
        ``<archive_base>/gis/20131011/T1250_TOLI_20131011115618.dat``

        **Args:**
            file: the inbound GIS WebMethods T1250 file.

        **Returns:**
            string representation of the absolute path to the *file*'s
            archive target

        """
        customer = self.config.pe_customer
        filename = os.path.basename(file)
        archive_dir = None
        m = re.search(self.config.pe_in_file_archive_string, filename)
        if m is not None:
            file_timestamp = m.group(1)
            dir = os.path.join(self.config.archive_dir,
                               customer,
                               file_timestamp)
            archive_dir = os.path.join(dir, filename)

        return archive_dir
