#!/usr/bin/python

import os
import inspect
from optparse import OptionParser

import nparcel
from nparcel.utils.log import log, set_log_level, suppress_logging


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
    np = nparcel.Daemon(pidfile='/var/tmp/nparceld.pid',
                        file=file,
                        dry=dry)

    script_name = inspect.getfile(inspect.currentframe())
    scrip_name = os.path.basename(script_name)
    if args[0] == 'start':
        if dry:
            print('Starting %s inline ...' % script_name)
            np._start(np.exit_event)
        else:
            print('Starting %s as daemon ...' % script_name)
            np.start()
    elif args[0] == 'stop':
        suppress_logging()
        print('Stopping %s ...' % script_name)
        np.stop()
        print('OK')

if __name__ == '__main__':
    main()
