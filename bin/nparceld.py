#!/usr/bin/python

import nparcel
from nparcel.utils.log import log

KWARGS = {'driver': 'FreeTDS',
          'host': 'SQVDBAUT07',
          'database': 'Nparcel',
          'user': 'npscript',
          'password': 'UX3O5#ujn-dk',
          'port': 1442}


def main():
    """
    """
    loader = nparcel.Loader(db=KWARGS)
    reporter = nparcel.Reporter()

    file = 'T1250_TOLP_20130413135756.txt'

    log.info('Processing file: "%s" ...' % file)
    try:
        f = open(file, 'r')

        reporter.reset()
        loader.reset()
        for line in f:
            record = line.rstrip('\r\n')
            if record == '%%EOF':
                log.info('EOF found')
                reporter.end()
                reporter.set_failed_log(loader.alerts)
                reporter.report()
            else:
                reporter(loader.process(record))

        f.close()
    except IOError, e:
        log.error('Error opening file "%s": %s' % (file, str(e)))

if __name__ == '__main__':
    main()
