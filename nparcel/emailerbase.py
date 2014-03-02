__all__ = [
    "EmailerBase",
]
import re
import os

from nparcel.utils.log import log


class EmailerBase(object):
    """Base email class.

    .. attribute:: template_base
        directory where templates are read from

    """
    _facility = None
    _template_base = os.path.join(os.path.expanduser('~'),
                                  '.nparceld',
                                  'templates')

    def __init__(self, template_base=None):
        """Base emailer initialiser.
        """
        self._facility = self.__class__.__name__

        if template_base is not None:
            self._template_base = template_base

    @property
    def template_base(self):
        return self._template_base

    def set_template_base(self, value):
        self._template_base = value
        log.debug('%s template_base set to "%s"' %
                  (self._facility, self.template_base))

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
