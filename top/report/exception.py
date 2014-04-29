__all__ = [
    "Exception",
]
import nparcel
from nparcel.utils.log import log


class Exception(nparcel.Auditer):
    """Toll Parcel Portal Exception class.

    """
    def __init__(self, db_kwargs=None, delivery_partners=None):
        """Exception initialiser.

        """
        nparcel.Auditer.__init__(self,
                                 db_kwargs=db_kwargs,
                                 delivery_partners=delivery_partners)

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

        kwargs = {'delivery_partners': self.delivery_partners}
        sql = self.db.agent_stocktake.reference_exception_sql(**kwargs)
        self.db(sql)
        self.set_columns(self.db.columns())
        items = list(self.db.rows())

        cleansed_items = []
        for i in items:
            cleansed_items.append(self._cleanse(self.columns, i))

        log.info('Stocktake exception query complete')

        return cleansed_items
