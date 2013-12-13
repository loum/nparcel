__all__ = [
    "Uncollected",
]
import nparcel
from nparcel.utils.log import log


class Uncollected(nparcel.Auditer):
    """Toll Parcel Portal base Uncollected class.

    """
    def __init__(self, db_kwargs=None, bu_ids=None):
        """Uncollected initialiser.

        """
        super(nparcel.Uncollected, self).__init__(db_kwargs=db_kwargs,
                                                  bu_ids=bu_ids)

    def process(self, id, dry=False):
        """Checks ``agent_stocktake`` table for items that exist
        in the Toll Parcel Portal and are uncollected and aged.

        **Kwargs:**
            *dry*: do not execute, only report

        **Returns:**
            list of ``job_item`` IDs that have been reported uncollected
            by the Agent and qualify as being aged in the Toll Parcel
            Point database.

        """
        log.info('Uncollected (Aged) query for BU ID "%d" ...' % id)

        log.debug('Setting processed_ts column')
        ts_now = self.db.date_now()
        if not dry:
            sql = self.db.agent_stocktake.update_processed_ts_sql(ts_now)
            self.db(sql)
            self.db.commit()

        aged_jobitems = []

        sql = self.db.jobitem.reference_sql(bu_ids=(id,))
        self.db(sql)

        self.set_columns(self.db.columns())
        for i in self.db.rows():
            log.debug('Found job_item: %s' % str(i))
            aged_jobitems.append(i)

        cleansed_jobitems = []
        for i in aged_jobitems:
            cleansed_jobitems.append(self._cleanse(self.columns, i))

        translated_aged_jobitems = []
        for i in cleansed_jobitems:
            translated_aged_jobitems.append(self._translate_bu(self.columns,
                                                               i,
                                                               self.bu_ids))

        date_delta_jobitems = []
        for i in translated_aged_jobitems:
            delta_row = self.add_date_diff(self.columns,
                                           i,
                                           self.delta_time_column,
                                           ts_now)
            date_delta_jobitems.append(delta_row)

        tmp_hdrs_list = self.db.columns()
        tmp_hdrs_list.append('DELTA_TIME')
        self.set_columns(tmp_hdrs_list)

        return date_delta_jobitems
