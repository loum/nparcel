#!/usr/bin/python

from optparse import OptionParser

import nparcel
from nparcel.utils.log import log

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
    parser.add_option('-f', '--file',
                      dest='file',
                      help='file to process inline')
    parser.add_option('-d', '--dry',
                      dest='dry',
                      action='store_true',
                      help='dry run - show what would have been done')
    (options, args) = parser.parse_args()

    file = None
    if options.file:
        file = options.file

    dry = options.dry is not None
    log.info('Processing dry run %s' % dry)

    start(file=file, dry=dry)


def start(file=None, dry=False):
    loader = nparcel.Loader(db=KWARGS)
    #loader = nparcel.Loader()
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
                        reporter(loader.process(record))
                f.close()

            except IOError, e:
                log.error('Error opening file "%s": %s' % (file, str(e)))
        else:
            log.error('ODBC connection failure -- aborting')

if __name__ == '__main__':
    main()
