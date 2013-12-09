__all__ = [
    "Compliance",
]
import nparcel
from nparcel.utils.log import log


class Compliance(nparcel.Auditer):
    """Toll Parcel Portal base Compliance class.

    .. attribute::
        *columns*: list of names of the query columns

    .. attribute::
        *delta_time_column*: raw column name to use for time delta
        (default ``JOB_TS`` which relates to the ``job.job_ts`` column)

    """
    _columns = []
    _delta_time_column = 'JOB_TS'

    def __init__(self, db_kwargs=None):
        """Compliance initialiser.

        """
        super(nparcel.Compliance, self).__init__(db_kwargs=db_kwargs)

    @property
    def columns(self):
        return self._columns

    def set_columns(self, values=None):
        del self._columns[:]
        self._columns = []

        if values is not None:
            log.debug('Setting columns to "%s"' % values)
            self._columns.extend(values)
        else:
            log.debug('Cleared columns list')

    @property
    def delta_time_column(self):
        return self._delta_time_column

    def set_delta_time_column(self, value):
        self._delta_time_column = value
        log.debug('Set delta time column to "%s"' % self._delta_time_column)

    def process(self, id=None, dry=False):
        """Checks ``agent_stocktake`` table for agents that have not
        completed a stocktake in the current period.

        **Kwargs:**
            *dry*: do not execute, only report

        **Returns:**
            list of ``agent_stocktake`` IDs of agents that have not
            performed a stocktake in the current period.

        """
        log.info('Agent compliance query ...')

        agents = []

        log.info('Agent compliance query complete')

        return agents
