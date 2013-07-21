#!/usr/bin/python
import sys
import time
import datetime
import signal
from optparse import OptionParser

import nparcel.utils
from nparcel.utils.log import log


class DummyDaemon(nparcel.utils.Daemon):

    def __init__(self, pidfile):
        self.fh = None
        super(DummyDaemon, self).__init__(pidfile=pidfile)

    def _start(self, event):
        # Prepare the environment to handle SIGTERM.
        signal.signal(signal.SIGTERM, self._exit_handler)
        self.fh = open('/var/tmp/dummy.out', 'w')

        while True:
            self.fh.write('%s\n' % str(datetime.datetime.now().isoformat(' ')))
            self.fh.flush()
            time.sleep(1)

    def _exit_handler(self, signal, frame):
        self.fh.close()
        log_msg = '%s --' % type(self).__name__
        log.info('%s SIGTERM intercepted' % log_msg)
        sys.exit(0)


def main():
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
        action = args[0]

    x = DummyDaemon(pidfile='/var/tmp/dummy.pid')
    if args[0] == 'start':
        x.start()
    elif args[0] == 'stop':
        x.stop()

if __name__ == "__main__":
    main()
