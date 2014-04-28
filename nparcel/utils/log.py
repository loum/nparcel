__all__ = [
    "log",
    "set_log_level",
    "suppress_logging",
    "set_console",
    "rollover",
]

import logging
import logging.config
import os
import datetime
import inspect


"""Configuration file for the logging module can be provided in the
following locations:

  * Local directory - `./log.conf`
  * User's home directory - `~user/log.conf`
  * A standard system-wide directory - `/etc/myproject/myproject.conf`
  * A place named by an environment variable `LOG_CONF`
  * The `conf` directory of the `utils` package distribution ("utils/conf")

This arrangement is analogous to "rc" files.  for example, "bashrc",
"vimrc", etc.
"""

locations = [
    os.environ.get("LOG_CONF"),
    os.curdir,
    os.path.expanduser("~"),
    os.path.join(os.path.expanduser("~"), '.top'),
]

found_log_config = False
for loc in locations:
    try:
        source = open(os.path.join(loc, "log.conf"))
        logging.config.fileConfig(source)
        source.close()
        found_log_config = True
        break
    except Exception, err:
        pass

# Holy crap!  Some black magic to identify logger handlers ...
# The calling script will be the outermost call in the stack.  Parse the
# resulting frame to get the name of the script.
logger_name = None
if found_log_config:
    s = inspect.stack()
    logger_name = os.path.basename(s[-1][1])
    if logger_name == 'nosetests' or logger_name == '<stdin>':
        logger_name = None


log = logging.getLogger(logger_name)
if logger_name is not None:
    # Contain logging to the configured handler only (not console).
    log.propagate = False

if not found_log_config:
    # If no config, just dump a basic log message to console.
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s:: %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.level = logging.NOTSET


def set_console():
    """Drop back to the root logger handler.
    """
    for hdlr in log.handlers:
        log.removeHandler(hdlr)
    log.propagate = False

    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s:: %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.level = logging.NOTSET


def rollover():
    """Specific to a TimedRotatingFileHandler, will force a rollover of the
    logs as per the requirements outlined in the logging configuration.

    """
    # Check if we can identify a handler log file from the logger_name.
    log.debug('Checking for a log rollover event')
    logger_handler = None
    for handler in log.handlers:
        if not isinstance(handler,
                          logging.handlers.TimedRotatingFileHandler):
            log.debug('Not a TimedRotatingFileHandler -- skip rollover')
            continue

        # Try to match the logger_name with the log filename.
        log_file = os.path.basename(handler.baseFilename)
        logger_from_file = os.path.splitext(log_file)[0]

        if (logger_name == logger_from_file and
            isinstance(handler, logging.handlers.TimedRotatingFileHandler)):
            logger_handler = handler
            break

    if logger_handler is not None:
        # OK, we have found our handler, check if a backup already exists.
        now = datetime.datetime.now()
        today_logfile = ("%s.%s" % (logger_handler.baseFilename,
                                    now.strftime("%Y-%m-%d")))
        backup_time = now - datetime.timedelta(days=1)
        backup_logfile = ("%s.%s" % (logger_handler.baseFilename,
                                     backup_time.strftime("%Y-%m-%d")))

        # Rollover only if a backup has not already been made.
        # This includes a backup of today.
        log.debug('Checking if backup logs "%s/%s" exist' %
                   (backup_logfile, today_logfile))
        if (not os.path.exists(backup_logfile) and
            not os.path.exists(today_logfile)):
            log.info('Forcing rollover of log: "%s"' %
                     logger_handler.baseFilename)
            handler.doRollover()


def set_log_level(level='INFO'):
    """
    """
    level_map = {
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }

    log.setLevel(level_map[level])


def suppress_logging():
    """
    """
    logging.disable(logging.ERROR)


def enable_logging():
    """
    """
    logging.disable(logging.NOTSET)


def autolog(message):
    """Automatically log the current function details.

    """
    if log.isEnabledFor(logging.DEBUG):
        # Get the previous frame in the stack.
        # Otherwise it would be this function!!!
        f = inspect.currentframe().f_back.f_code
        lineno = inspect.currentframe().f_back.f_lineno

        # Dump the message function details to the log.
        log.debug("%s: %s in %s:%i" % (message,
                                       f.co_name,
                                       f.co_filename,
                                       lineno))
