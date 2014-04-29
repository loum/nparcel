__all__ = [
    "Compliance",
]
import top
from top.utils.log import log


class Compliance(top.Auditer):
    """Toll Outlet Portal base Compliance class.

    .. attribute:: period

        time (in days) from now that is the cut off for agent compliance
        (default 7 days)

    """
    _period = 7

    def __init__(self, db_kwargs=None, delivery_partners=None):
        """Compliance initialiser.

        """
        top.Auditer.__init__(self,
                                 db_kwargs=db_kwargs,
                                 delivery_partners=delivery_partners)

    @property
    def period(self):
        return self._period

    def set_period(self, value):
        self._period = value
        log.debug('Compliance period set to "%s"' % self.period)

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

        kwargs = {'period': self.period,
                  'delivery_partners': self.delivery_partners}
        sql = self.db.jobitem.agent_id_of_aged_parcels(**kwargs)
        self.db(sql)
        self.set_columns(self.db.columns())
        agents = list(self.db.rows())

        cleansed_agents = []
        for i in agents:
            cleansed_agents.append(self._cleanse(self.columns, i))

        log.info('Agent compliance query complete')

        return cleansed_agents
