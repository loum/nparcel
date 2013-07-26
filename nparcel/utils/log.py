__all__ = [
    "log",
    "set_log_level",
    "suppress_logging",
    "set_console_logger",
]

import logging
import logging.config
import os
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
    os.curdir,
    os.path.expanduser("~"),
    "/etc/myproject",
    os.environ.get("LOG_CONF"),
]

for loc in locations:
    try:
        source = open(os.path.join(loc, "log.conf"))
        logging.config.fileConfig(source)
        source.close()
    except:
        pass

log = logging.getLogger()


def set_log_level(level='INFO'):
    """
    """
    level_map = {
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
    }

    log.setLevel(level_map[level])


def suppress_logging():
    """
    """
    logging.disable(logging.ERROR)


def autolog(message):
    """Automatically log the current function details.

    """
    if log.isEnabledFor(logging.DEBUG):
        # Get the previous frame in the stack.
        # Otherwise it would be this function!!!
        f = inspect.currentframe().f_back.f_code
        lineno = inspect.currentframe().f_back.f_lineno

        # Dump the message function details to the log.
        logging.debug("%s: %s in %s:%i" % (message,
                                           f.co_name,
                                           f.co_filename,
                                           lineno))
