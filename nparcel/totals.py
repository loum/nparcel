__all__ = [
    "Totals",
]
import nparcel
from nparcel.utils.log import log


class Totals(nparcel.Auditer):
    """Toll Parcel Portal base Totals class.

    .. attribute:: period

        time (in days) from now that is the cut off for agent totals
        (default 7 days)

    """
    _period = 7

    def __init__(self, db_kwargs=None):
        """Totals initialiser.

        """
        super(nparcel.Totals, self).__init__(db_kwargs=db_kwargs)

    @property
    def period(self):
        return self._period

    def set_period(self, value):
        self._period = value
        log.debug('Totals period set to "%s"' % self.period)

    def process(self, id=None, dry=False):
        """Checks ``agent_stocktake`` table parcel counts against
        the parcel counts registered in Toll Parcel Portal.

        **Kwargs:**
            *dry*: do not execute, only report

        **Returns:**
            list of ``agent_stocktake`` ADP parcel counts and
            that Agents Toll Parcel Portal count.

        """
        log.info('Parcel totals query ...')

        sql = self.db.jobitem.total_agent_stocktake_parcel_count_sql(id)
        self.db(sql)
        self.set_columns(self.db.columns())
        agents = list(self.db.rows())

        log.info('Agent parcel totals query complete')

        return agents
