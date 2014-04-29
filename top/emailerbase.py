__all__ = [
    "EmailerBase",
]
import re
import os
import socket

from top.utils.log import log


class EmailerBase(object):
    """Base email class.

    .. attribute:: template_base
        directory where templates are read from

    .. attribute:: hostname

        string containing the hostname of the machine where the Python
        interpreter is currently executing

    """
    _facility = None
    _hostname = socket.gethostname()
    _template_base = os.path.join(os.path.expanduser('~'),
                                  '.top',
                                  'templates')

    def __init__(self, template_base=None):
        """Base emailer initialiser.
        """
        self._facility = self.__class__.__name__

        if template_base is not None:
            self._template_base = template_base

    @property
    def facility(self):
        return self._facility

    @property
    def template_base(self):
        return self._template_base

    def set_template_base(self, value):
        self._template_base = value
        log.debug('%s template_base set to "%s"' %
                  (self.facility, self.template_base))

    @property
    def hostname(self):
        return self._hostname

    def set_hostname(self, value):
        self._hostname = value
        log.debug('%s hostname set to "%s"' %
                  (self.facility, self.hostname))

    def validate(self, email):
        """Validate the *email* address.

        Runs a simple regex validation across the *email* address is

        **Args:**
            email: the email address to validate

        **Returns:**
            boolean ``True`` if the email validates

            boolean ``False`` if the email does not validate

        """
        status = True

        err = 'Email "%s" validation:' % email
        ex = '^[a-zA-Z0-9._%\-+]+@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,6}$'
        r = re.compile(ex)
        m = r.match(email)
        if m is None:
            status = False
            log.error('%s Failed' % err)
        else:
            log.info('%s OK' % err)

        return status
