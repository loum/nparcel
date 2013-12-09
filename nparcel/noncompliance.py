__all__ = [
    "NonCompliance",
]
import nparcel
from nparcel.utils.log import log


class NonCompliance(nparcel.Auditer):
    """Toll Parcel Portal base NonCompliance class.

    """

    def __init__(self, db_kwargs=None):
        """NonCompliance initialiser.

        """
        super(nparcel.NonCompliance, self).__init__(db_kwargs=db_kwargs)

    def process(self, id=None, dry=False):
        """Identifies list of ``job_items`` found in Toll Parcel Portal
        but not scanned into ``agent_stocktake`` by the agent.

        **Kwargs:**
            *dry*: do not execute, only report

        **Returns:**
            list of ``job_items`` found in Toll Parcel Portal but not
            scanned into ``agent_stocktake``.

        """
        log.info('Stocktake non-compliance query ...')

        #sql = self.db.agent_stocktake.compliance_sql(period=self.period)
        #self.db(sql)
        #self.set_columns(self.db.columns())
        #agents = list(self.db.rows())
        job_items = []

        log.info('Stocktake non-compliance query complete')

        return job_items
