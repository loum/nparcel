#!/usr/bin/python

import re
import time
import datetime
from optparse import OptionParser

import nparcel
from nparcel.utils.log import log, set_log_level

KWARGS = {'driver': 'FreeTDS',
          'host': 'SQVDBAUT07',
          'database': 'Nparcel',
          'user': 'npscript',
          'password': 'UX3O5#ujn-dk',
          'port': 1442}


class NparcelDaemon(nparcel.utils.Daemon):

    def __init__(self,
                 pidfile,
                 file=None,
                 dry=False):
        self.file = file
        self.dry = dry
        super(NparcelDaemon, self).__init__(pidfile=pidfile)

    def _start(self, event):
        loader = nparcel.Loader(db=KWARGS)
        #loader = nparcel.Loader()
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
                    file_timestamp = validate_file(file)

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


def main():
    """Nparcel daemoniser.
    """
    usage = "usage: %prog [options] start|stop|status"
    parser = OptionParser(usage=usage)
    parser.set_usage
    parser.add_option("-v", "--verbose",
                      dest="verbose",
                      action="count",
                      default=0,
                      help="raise logging verbosity")
    parser.add_option('-f', '--file',
                      dest='file',
                      help='file to process inline')
    parser.add_option('-d', '--dry',
                      dest='dry',
                      action='store_true',
                      help='dry run - show what would have been done')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
        action = args[0]

    # Enable detailed logging if required.
    if options.verbose == 0:
        set_log_level('INFO')
        log.info('Logging verbosity set to "INFO" level')

    # Check if a filename was provided on the command line.
    file = None
    if options.file:
        file = options.file

    # Commit to the DB?
    dry = options.dry is not None
    log.info('Processing dry run %s' % dry)

    # OK, start processing.
    np = NparcelDaemon(pidfile='/var/tmp/nparceld.pid',
                       file=file,
                       dry=dry)
    log.debug('have args: %s' % str(args))
    if args[0] == 'start':
        #np._start(file=file, dry=dry)
        log.debug('starting loader')
        np.start()
    elif args[0] == 'stop':
        log.debug('stopping loader')
        np.stop()


def validate_file(filename=None):
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

if __name__ == '__main__':
    main()
