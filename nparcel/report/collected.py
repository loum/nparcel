__all__ = [
    "Collected",
]
import nparcel
from nparcel.utils.log import log


class Collected(nparcel.Auditer):
    """Toll Parcel Portal base Collected class.

    """
    def __init__(self, db_kwargs=None, bu_ids=None):
        """Collected initialiser.

        """
        super(nparcel.Collected, self).__init__(db_kwargs=db_kwargs,
                                                bu_ids=bu_ids)

    def process(self, id, dry=False):
        """Checks ``agent_stocktake`` table for items that have already
        have been flagged as collected in Toll Parcel Portal.

        **Args:**
            *id*: tuple of integer based values relating to the
            ``job.bu_id`` column

        **Kwargs:**
            *dry*: do not execute, only report

        **Returns:**
            list of ``job_item`` IDs that have been reported uncollected
            by the Agent yet exist in Toll Parcel Point database as being
            collected.

        """
        log.info('Collected Agent Stocktake query ...')

        sql = self.db.jobitem.reference_sql(bu_ids=id, picked_up=True)
        self.db(sql)

        self.set_columns(self.db.columns())
        items = list(self.db.rows())

        cleansed_items = []
        for i in items:
            cleansed_items.append(self._cleanse(self.columns, i))

        translated_aged_items = []
        for i in cleansed_items:
            translated_aged_items.append(self._translate_bu(self.columns,
                                                            i,
                                                            self.bu_ids))

        return translated_aged_items
