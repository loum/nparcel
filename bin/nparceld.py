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


def main():
    """Nparcel daemoniser.
    """
    parser = OptionParser()
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
    start(file=file, dry=dry)


def start(file=None, dry=False):
    #loader = nparcel.Loader(db=KWARGS)
    loader = nparcel.Loader()
    reporter = nparcel.Reporter()

    commit = True
    if dry:
        commit = False

    files = []
    if file is not None:
        files.append(file)

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
