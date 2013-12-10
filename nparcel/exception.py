__all__ = [
    "Exception",
]
import nparcel
from nparcel.utils.log import log


class Exception(nparcel.Auditer):
    """Toll Parcel Portal base Exception class.

    """
    def __init__(self, db_kwargs=None):
        """Exception initialiser.

        """
        super(nparcel.Exception, self).__init__(db_kwargs=db_kwargs)

    def process(self, id=None, dry=False):
        """Checks ``agent_stocktake`` table for scanned items that
        do not exist in the Toll Parcel Portal.

        **Kwargs:**
            *dry*: do not execute, only report

        **Returns:**
            list of ``agent_stocktake`` IDs of agents that have not
            performed a stocktake in the current period.

        """
        log.info('Stocktake exception query ...')

        #sql = self.db.agent_stocktake.compliance_sql(period=self.period)
        #self.db(sql)
        #self.set_columns(self.db.columns())
        #agents = list(self.db.rows())
        items = []

        log.info('Stocktake exception query complete')

        return items
