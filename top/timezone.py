__all__ = [
    "convert_timezone",
]
import time
import pytz
import datetime

from top.utils.log import log


TZ = {'vic': 'Australia/Victoria',
      'nsw': 'Australia/NSW',
      'qld': 'Australia/Queensland',
      'sa': 'Australia/South',
      'wa': 'Australia/West',
      'act': 'Australia/ACT',
      'tas': 'Australia/Tasmania',
      'nt': 'Australia/North'}

_local_tz = TZ.get('vic')


def convert_timezone(time_string,
                     state,
                     time_format='%Y-%m-%d %H:%M:%S',
                     time_tz_format='%Y-%m-%d %H:%M:%S %Z%z'):
    """Will parse the *time_string* and attempt to localise the
    timezone against *state*.

    *Args*:
        *time_string*: the ISO formated date string.  For example::

            2013-11-25 09:51:00

        .. note::

            the time string parser expects the time in this format.

        *state*: the Australian state to localise the timezone against

        *time_format*: format string used to display the date

        *time_format*: alternate format string with explicit timezone
        information

    *Returns*:

        localised date string or *time_string* if *state* is invalid

    """
    log.debug('Timezone conversion for "%s/%s": ' %
              (str(time_string), state))
    time_string = str(time_string).split('.')[0]

    log.info('Localising timezone for time "%s" against state: "%s"' %
                (time_string, state))

    tz_time_string = time_string
    parsed_time = time.strptime(time_string, '%Y-%m-%d %H:%M:%S')
    dt = datetime.datetime.fromtimestamp(time.mktime(parsed_time))
    local_dt = pytz.timezone(_local_tz).localize(dt)

    state_tz = TZ.get(state.lower())
    if state_tz is not None:
        tz = pytz.timezone(state_tz)
        dt = tz.normalize(local_dt.astimezone(tz))
        tz_time_string = dt.strftime(time_format)
        log.info('"%s" localised to "%s"' %
                    (time_string, dt.strftime(time_tz_format)))
    else:
        log.warn('Unable to determine TZ for state: "%s"' %
                    state.upper())

    return tz_time_string
