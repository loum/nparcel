from daemon import Daemon, DaemonError

""":mod:`nparcel.utils` is a handy kit of commonly used utilities.

Do you find yourself doing the same thing over and (yawn) over again?  Then
create a definition in this package and make your life that much easier ...

"""
__all__ = [
    "Utils",
]
import datetime
import time

from nparcel.utils.log import log


def date_diff(start_date, end_date, precision='days'):
    """Calculates the difference between *start_date* and *end_date*.

    Value returned is based on *precision* which defaults to days.  Days
    are the only precesion supported at the moment.

    For example, if the start date is the ISO formatted string
    ``2013-12-05 00:00:00`` and the *end_date* is ``2013-12-06 12:00:00``
    then the difference in days is ``1.5``.

    .. note::

        Microseconds are stripped before processing.

    **Args:**
        *start_date* and *end_date*: ISO formatted dates in the form::

            %Y-%m-%d %H:%M:%S

    **Returns:**
        integer value representing the time delta

    """
    delta = None

    start_t = end_t = None

    if isinstance(start_date, datetime.datetime):
        start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(end_date, datetime.datetime):
        end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")

    try:
        start_usec_stripped = start_date.split('.', 1)[0]
        start_t = time.strptime(start_usec_stripped, '%Y-%m-%d %H:%M:%S')
        end_usec_stripped = end_date.split('.', 1)[0]
        end_t = time.strptime(end_usec_stripped, '%Y-%m-%d %H:%M:%S')
    except ValueError, err:
        log.warn('Unable to parse date: "%s"' % err)

    if start_t is not None and end_t is not None:
        start_dt = datetime.datetime.fromtimestamp(time.mktime(start_t))
        end_dt = datetime.datetime.fromtimestamp(time.mktime(end_t))
        delta_dt = end_dt - start_dt

        delta = None
        if precision == 'days':
            delta = delta_dt.days

    log.debug('Time delta (%s) between "%s" and "%s": %s' % (precision,
                                                             start_date,
                                                             end_date,
                                                             str(delta)))

    return delta
