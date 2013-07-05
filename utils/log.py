__all__ = [
    "log",
    "set_log_level",
    "suppress_logging",
]

import logging
import logging.config
import os
import functools
import types
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
    os.path.join("utils", "conf")
]

for loc in locations:
    try:
        with open(os.path.join(loc, "log.conf")) as source:
            logging.config.fileConfig(source)
    except:
        pass

log = logging.getLogger()

def logger(f):
    def wrapper():
        log.info('starting %s' % f.__name__)
        f()
        log.info('ending %s' % f.__name__)

    return wrapper

def class_logging(c):
    """Class decorator that adds logging to all "public" class methods.
    """
    method_p = lambda m: not m.startswith('_') and \
                         isinstance(getattr(c, m), types.MethodType)
    public_methods = filter(method_p, dir(c))
 
    for method_name in public_methods:
        class_method = getattr(c, method_name)
 
        def helper(mname, method):
            @functools.wraps(method)
            def wrapper(*a, **kw):
                msg = '{0}({1}, {2})'.format(mname, a, kw)
                log.debug(msg)
                try:
                    response = method(*a, **kw)
                except Exception as e:
                    error_message = 'no additional information'
                    if hasattr(e, 'args'):
                        error_message = str(e)
                    msg = '{0} raised {1}, {2}'.format(mname,
                                                       type(e),
                                                       error_message)
                    log.debug(msg)
                    raise
                else:
                    msg = '{0} returned {1}'.format(mname, response)
                    log.debug(msg)
 
                return response
            return wrapper
         
        fn = types.MethodType(helper(method_name, class_method), None, c)
        setattr(c, method_name, fn)

    return c

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
