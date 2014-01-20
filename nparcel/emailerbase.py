__all__ = [
    "EmailerBase",
]
import re

from nparcel.utils.log import log


class EmailerBase(object):
    """Base email class.

    """
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
