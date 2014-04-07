__all__ = [
    "PodTranslator",
]
import nparcel
import time

from nparcel.utils.log import log


class PodTranslator(nparcel.Service):
    """:class:`nparcelPodTranslator` object structure.
    """

    def __init__(self):
        nparcel.Service.__init__(self)

    def token_generator(self, dt=None):
        """Highly customised token generator that provides a unique,
        unambiguous numeric representation for a POD identifier.

        Seconds since epoch maintains a natural counter.  Token can be
        forced from a know :class:`datetime.datetime` object via the *dt*
        parameter.  Otherwise, if *dt* is ``None`` token generation is
        based on current time.

        **Kwargs:**
            *dt*: a :class:`datetime.datetime` object to override the token
            generator against.

        **Returns:**
            token representation of seconds since epoch that can be used
            in an unambiguous arrangement with ``job_item.id`` for POD
            naming

        """
        token = None

        epoch = 0
        if dt is not None:
            # Get the microsecond component.
            us = dt.microsecond / 1E6
            epoch = int((time.mktime(dt.timetuple()) + us) * 10)
        else:
            # Guarantee, sequential uniqueness.
            time.sleep(0.5)
            epoch = int(time.time() * 10)

        if epoch > 0:
            # Check that it's not above our threshold.
            if epoch < 20000000000:
                token = map(int, str(epoch))
                token[0] = 0
                token = ''.join(str(x) for x in token)
            else:
                log.error('Maximum seconds threshold breached: %d' % epoch)

        log.debug('Token value generated: "%s"' % token)
        return token
