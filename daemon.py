__all__ = [
    "Daemon",
]
import re
import time
import datetime
import nparcel

from nparcel.utils.log import log

KWARGS = {'driver': 'FreeTDS',
          'host': 'SQVDBAUT07',
          'database': 'Nparcel',
          'user': 'npscript',
          'password': 'UX3O5#ujn-dk',
          'port': 1442}


class Daemon(nparcel.utils.Daemon):

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False):
        self.file = file
        self.dry = dry
        super(Daemon, self).__init__(pidfile=pidfile)

    def _start(self, event):
        #loader = nparcel.Loader(db=KWARGS)
        loader = nparcel.Loader()
        reporter = nparcel.Reporter()

        commit = True
        if self.dry:
            commit = False

        files = []
        if self.file is not None:
            files.append(self.file)

        log.info('Processing files: "%s" ...' % str(files))

        for file in files:
            log.info('Processing file: "%s" ...' % file)

            if loader.db():
                try:
                    f = open(file, 'r')
                    file_timestamp = self.validate_file(file)

                    reporter.reset()
                    for line in f:
                        record = line.rstrip('\r\n')
                        if record == '%%EOF':
                            log.info('EOF found')
                            loader.reset(commit=commit)
                            reporter.end()
                            reporter.set_failed_log(loader.alerts)
                            reporter.report()
                        else:
                            reporter(loader.process(file_timestamp, record))
                    f.close()

                except IOError, e:
                    log.error('Error opening file "%s": %s' % (file, str(e)))
            else:
                log.error('ODBC connection failure -- aborting')

            time.sleep(30)

    def _exit_handler(self, signal, frame):
        log_msg = '%s --' % type(self).__name__
        log.info('%s SIGTERM intercepted' % log_msg)

    def validate_file(self, filename=None):
        """
        """
        log.debug('Validating filename: "%s"' % filename)
        m = re.search('T1250_TOL._(\d{14})\.txt', filename)
        file_timestamp = m.group(1)

        parsed_time = time.strptime(file_timestamp, "%Y%m%d%H%M%S")
        log.debug('parsed_time: %s' % parsed_time)
        dt = datetime.datetime.fromtimestamp(time.mktime(parsed_time))
        dt_formatted = dt.isoformat(' ')

        return dt_formatted
