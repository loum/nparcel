__all__ = [
    "NonCompliance",
]
import nparcel
from nparcel.utils.log import log


class NonCompliance(nparcel.Auditer):
    """Toll Parcel Portal base NonCompliance class.

    """

    def __init__(self, db_kwargs=None, bu_ids=None):
        """NonCompliance initialiser.

        """
        super(nparcel.NonCompliance, self).__init__(db_kwargs=db_kwargs,
                                                    bu_ids=bu_ids)

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

        jobitems = []
        xlated_jobitems = []

        bu_ids = tuple(self.bu_ids.keys())
        if len(bu_ids):
            sql = self.db.jobitem.non_compliance_sql(bu_ids=bu_ids)
            self.db(sql)
            self.set_columns(self.db.columns())
            jobitems = list(self.db.rows())

            xlated_jobitems = []
            for i in jobitems:
                xlated_jobitems.append(self._translate_bu(self.columns,
                                                          i,
                                                          self.bu_ids))
        else:
            log.warn('No BU IDs specified')

        log.info('Stocktake non-compliance query complete')

        return xlated_jobitems
